# Copyright The IETF Trust 2007, All Rights Reserved
import email
from rexec import FileWrapper

import datetime
import os
import xml2rfc

from django.conf import settings
from django.contrib import messages
from django.core.urlresolvers import reverse as urlreverse
from django.core.validators import validate_email, ValidationError
from django.http import HttpResponseRedirect, Http404, HttpResponseForbidden, \
    HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.module_loading import import_string

import debug                            # pyflakes:ignore

from ietf.doc.models import Document, DocAlias
from ietf.doc.utils import prettify_std_name
from ietf.group.models import Group
from ietf.ietfauth.utils import has_role, role_required
from ietf.ipr.mail import get_reply_to
from ietf.mailtrigger.utils import gather_address_lists
from ietf.message.models import Message
from ietf.submit.forms import SubmissionUploadForm, NameEmailForm, EditSubmissionForm, PreapprovalForm, ReplacesForm, \
    SubmissionEmailForm, MessageModelForm
from ietf.submit.mail import send_full_url, send_approval_request_to_group, \
    send_submission_confirmation, send_manual_post_request, get_mail_contents, decode_text, \
    add_submission_email
from ietf.submit.models import Submission, SubmissionCheck, Preapproval, DraftSubmissionStateName, \
    SubmissionEmail, SubmissionEmailAttachment
from ietf.submit.utils import approvable_submissions_for_user, preapprovals_for_user, recently_approved_by_user
from ietf.submit.utils import validate_submission, create_submission_event
from ietf.submit.utils import docevent_from_submission
from ietf.submit.utils import post_submission, cancel_submission, rename_submission_files
from ietf.utils.accesstoken import generate_random_key, generate_access_token
from ietf.utils.draft import Draft
from ietf.utils.log import log
from ietf.utils.mail import send_mail_message


def upload_submission(request):
    if request.method == 'POST':
        try:
            form = SubmissionUploadForm(request, data=request.POST, files=request.FILES)
            if form.is_valid():
                authors = []
                file_name = {}
                abstract = None
                file_size = None
                for ext in form.fields.keys():
                    f = form.cleaned_data[ext]
                    if not f:
                        continue
                    
                    name = os.path.join(settings.IDSUBMIT_STAGING_PATH, '%s-%s.%s' % (form.filename, form.revision, ext))
                    file_name[ext] = name
                    with open(name, 'wb+') as destination:
                        for chunk in f.chunks():
                            destination.write(chunk)

                if form.cleaned_data['xml']:
                    if not form.cleaned_data['txt']:
                        file_name['txt'] = os.path.join(settings.IDSUBMIT_STAGING_PATH, '%s-%s.txt' % (form.filename, form.revision))
                        try:
                            pagedwriter = xml2rfc.PaginatedTextRfcWriter(form.xmltree, quiet=True)
                            pagedwriter.write(file_name['txt'])
                        except Exception as e:
                            raise ValidationError("Error from xml2rfc: %s" % e)
                        file_size = os.stat(file_name['txt']).st_size
                    # Some meta-information, such as the page-count, can only
                    # be retrieved from the generated text file.  Provide a
                    # parsed draft object to get at that kind of information.
                    with open(file_name['txt']) as txt_file:
                        form.parsed_draft = Draft(txt_file.read(), txt_file.name)

                else:
                    file_size = form.cleaned_data['txt'].size

                if form.authors:
                    authors = form.authors
                else:
                    # If we don't have an xml file, try to extract the
                    # relevant information from the text file
                    for author in form.parsed_draft.get_author_list():
                        full_name, first_name, middle_initial, last_name, name_suffix, email, company = author

                        line = full_name.replace("\n", "").replace("\r", "").replace("<", "").replace(">", "").strip()
                        email = (email or "").strip()

                        if email:
                            try:
                                validate_email(email)
                            except ValidationError:
                                email = ""

                        if email:
                            line += u" <%s>" % email

                        authors.append(line)

                if form.abstract:
                    abstract = form.abstract
                else:
                    abstract = form.parsed_draft.get_abstract()

                # save submission
                try:
                    submission = Submission.objects.create(
                        state=DraftSubmissionStateName.objects.get(slug="uploaded"),
                        remote_ip=form.remote_ip,
                        name=form.filename,
                        group=form.group,
                        title=form.title,
                        abstract=abstract,
                        rev=form.revision,
                        pages=form.parsed_draft.get_pagecount(),
                        authors="\n".join(authors),
                        note="",
                        first_two_pages=''.join(form.parsed_draft.pages[:2]),
                        file_size=file_size,
                        file_types=','.join(form.file_types),
                        submission_date=datetime.date.today(),
                        document_date=form.parsed_draft.get_creation_date(),
                        replaces="",
                        )
                except Exception as e:
                    log("Exception: %s\n" % e)
                    raise

                # run submission checkers
                def apply_check(submission, checker, method, fn):
                    func = getattr(checker, method)
                    passed, message, errors, warnings, items = func(fn)
                    check = SubmissionCheck(submission=submission, checker=checker.name, passed=passed, message=message, errors=errors, warnings=warnings, items=items)
                    check.save()

                for checker_path in settings.IDSUBMIT_CHECKER_CLASSES:
                    checker_class = import_string(checker_path)
                    checker = checker_class()
                    # ordered list of methods to try
                    for method in ("check_fragment_xml", "check_file_xml", "check_fragment_txt", "check_file_txt", ):
                        ext = method[-3:]
                        if hasattr(checker, method) and ext in file_name:
                            apply_check(submission, checker, method, file_name[ext])
                            break

                create_submission_event(request, submission, desc="Uploaded submission")
                docevent_from_submission(request, submission, desc="Uploaded new revision")

                return redirect("submit_submission_status_by_hash", submission_id=submission.pk, access_token=submission.access_token())
        except IOError as e:
            if "read error" in str(e): # The server got an IOError when trying to read POST data
                form = SubmissionUploadForm(request=request)
                form._errors = {}
                form._errors["__all__"] = form.error_class(["There was a failure receiving the complete form data -- please try again."])
            else:
                raise
        except ValidationError as e:
            form = SubmissionUploadForm(request=request)
            form._errors = {}
            form._errors["__all__"] = form.error_class(["There was a failure converting the xml file to text -- please verify that your xml file is valid.  (%s)" % e.message])
    else:
        form = SubmissionUploadForm(request=request)

    return render(request, 'submit/upload_submission.html',
                              {'selected': 'index',
                               'form': form})

def note_well(request):
    return render(request, 'submit/note_well.html', {'selected': 'notewell'})

def tool_instructions(request):
    return render(request, 'submit/tool_instructions.html', {'selected': 'instructions'})

def search_submission(request):
    error = None
    name = None
    if request.method == 'POST':
        name = request.POST.get('name', '')
        submission = Submission.objects.filter(name=name).order_by('-pk').first()
        if submission:
            return redirect(submission_status, submission_id=submission.pk)
        error = 'No valid submission found for %s' % name
    return render(request, 'submit/search_submission.html',
                              {'selected': 'status',
                               'error': error,
                               'name': name})

def can_edit_submission(user, submission, access_token):
    key_matched = access_token and submission.access_token() == access_token
    if not key_matched: key_matched = submission.access_key == access_token # backwards-compat
    return key_matched or has_role(user, "Secretariat")

def submission_status(request, submission_id, access_token=None):
    submission = get_object_or_404(Submission, pk=submission_id)

    key_matched = access_token and submission.access_token() == access_token
    if not key_matched: key_matched = submission.access_key == access_token # backwards-compat
    if access_token and not key_matched:
        raise Http404

    errors = validate_submission(submission)
    passes_checks = all([ c.passed!=False for c in submission.checks.all() ])

    is_secretariat = has_role(request.user, "Secretariat")
    is_chair = submission.group and submission.group.has_role(request.user, "chair")

    can_edit = can_edit_submission(request.user, submission, access_token) and submission.state_id == "uploaded"
    can_cancel = (key_matched or is_secretariat) and submission.state.next_states.filter(slug="cancel")
    can_group_approve = (is_secretariat or is_chair) and submission.state_id == "grp-appr"
    can_force_post = is_secretariat and submission.state.next_states.filter(slug="posted")
    show_send_full_url = not key_matched and not is_secretariat and submission.state_id not in ("cancel", "posted")

    addrs = gather_address_lists('sub_confirmation_requested',submission=submission)
    confirmation_list = addrs.to
    confirmation_list.extend(addrs.cc)

    requires_group_approval = (submission.rev == '00' and submission.group and submission.group.type_id in ("wg", "rg", "ietf", "irtf", "iab", "iana", "rfcedtyp") and not Preapproval.objects.filter(name=submission.name).exists())

    requires_prev_authors_approval = Document.objects.filter(name=submission.name)

    message = None

    if submission.state_id == "cancel":
        message = ('error', 'This submission has been canceled, modification is no longer possible.')
    elif submission.state_id == "auth":
        message = ('success', u'The submission is pending email authentication. An email has been sent to: %s' % ", ".join(confirmation_list))
    elif submission.state_id == "grp-appr":
        message = ('success', 'The submission is pending approval by the group chairs.')
    elif submission.state_id == "aut-appr":
        message = ('success', 'The submission is pending approval by the authors of the previous version. An email has been sent to: %s' % ", ".join(confirmation_list))


    submitter_form = NameEmailForm(initial=submission.submitter_parsed(), prefix="submitter")
    replaces_form = ReplacesForm(name=submission.name,initial=DocAlias.objects.filter(name__in=submission.replaces.split(",")))

    if request.method == 'POST':
        action = request.POST.get('action')
        if action == "autopost" and submission.state_id == "uploaded":
            if not can_edit:
                return HttpResponseForbidden("You do not have permission to perform this action")

            submitter_form = NameEmailForm(request.POST, prefix="submitter")
            replaces_form = ReplacesForm(request.POST, name=submission.name)
            validations = [submitter_form.is_valid(), replaces_form.is_valid()]
            if all(validations):
                submission.submitter = submitter_form.cleaned_line()
                replaces = replaces_form.cleaned_data.get("replaces", [])
                submission.replaces = ",".join(o.name for o in replaces)

                if requires_group_approval:
                    submission.state = DraftSubmissionStateName.objects.get(slug="grp-appr")
                    submission.save()

                    sent_to = send_approval_request_to_group(request, submission)

                    desc = "sent approval email to group chairs: %s" % u", ".join(sent_to)
                    docDesc = u"Request for posting approval emailed to group chairs: %s" % u", ".join(sent_to)

                else:
                    submission.auth_key = generate_random_key()
                    if requires_prev_authors_approval:
                        submission.state = DraftSubmissionStateName.objects.get(slug="aut-appr")
                    else:
                        submission.state = DraftSubmissionStateName.objects.get(slug="auth")
                    submission.save()

                    sent_to = send_submission_confirmation(request, submission)

                    if submission.state_id == "aut-appr":
                        desc = u"sent confirmation email to previous authors: %s" % u", ".join(sent_to)
                        docDesc = "Request for posting confirmation emailed to previous authors: %s" % u", ".join(sent_to)
                    else:
                        desc = u"sent confirmation email to submitter and authors: %s" % u", ".join(sent_to)
                        docDesc = "Request for posting confirmation emailed to submitter and authors: %s" % u", ".join(sent_to)

                msg = u"Set submitter to \"%s\", replaces to %s and %s" % (
                    submission.submitter,
                    ", ".join(prettify_std_name(r.name) for r in replaces) if replaces else "(none)",
                    desc)
                create_submission_event(request, submission, msg)
                docevent_from_submission(request, submission, docDesc)

                if access_token:
                    return redirect("submit_submission_status_by_hash", submission_id=submission.pk, access_token=access_token)
                else:
                    return redirect("submit_submission_status", submission_id=submission.pk)

        elif action == "edit" and submission.state_id == "uploaded":
            if access_token:
                return redirect("submit_edit_submission_by_hash", submission_id=submission.pk, access_token=access_token)
            else:
                return redirect("submit_edit_submission", submission_id=submission.pk)

        elif action == "sendfullurl" and submission.state_id not in ("cancel", "posted"):
            sent_to = send_full_url(request, submission)

            message = ('success', u'An email has been sent with the full access URL to: %s' % u",".join(confirmation_list))

            create_submission_event(request, submission, u"Sent full access URL to: %s" % u", ".join(sent_to))

        elif action == "cancel" and submission.state.next_states.filter(slug="cancel"):
            if not can_cancel:
                return HttpResponseForbidden('You do not have permission to perform this action')

            cancel_submission(submission)

            create_submission_event(request, submission, "Canceled submission")

            return redirect("submit_submission_status", submission_id=submission_id)


        elif action == "approve" and submission.state_id == "grp-appr":
            if not can_group_approve:
                return HttpResponseForbidden('You do not have permission to perform this action')

            post_submission(request, submission, "WG -00 approved")

            create_submission_event(request, submission, "Approved and posted submission")

            return redirect("doc_view", name=submission.name)


        elif action == "forcepost" and submission.state.next_states.filter(slug="posted"):
            if not can_force_post:
                return HttpResponseForbidden('You do not have permission to perform this action')

            if submission.state_id == "manual":
                desc = "Posted submission manually"
            else:
                desc = "Forced post of submission"

            post_submission(request, submission, desc)

            create_submission_event(request, submission, desc)

            return redirect("doc_view", name=submission.name)


        else:
            # something went wrong, turn this into a GET and let the user deal with it
            return HttpResponseRedirect("")

    return render(request, 'submit/submission_status.html', {
        'selected': 'status',
        'submission': submission,
        'errors': errors,
        'passes_checks': passes_checks,
        'submitter_form': submitter_form,
        'replaces_form': replaces_form,
        'message': message,
        'can_edit': can_edit,
        'can_force_post': can_force_post,
        'can_group_approve': can_group_approve,
        'can_cancel': can_cancel,
        'show_send_full_url': show_send_full_url,
        'requires_group_approval': requires_group_approval,
        'requires_prev_authors_approval': requires_prev_authors_approval,
        'confirmation_list': confirmation_list,
    })


def edit_submission(request, submission_id, access_token=None):
    submission = get_object_or_404(Submission, pk=submission_id, state="uploaded")

    if not can_edit_submission(request.user, submission, access_token):
        return HttpResponseForbidden('You do not have permission to access this page')

    errors = validate_submission(submission)
    form_errors = False

    # we split the form handling into multiple forms, one for the
    # submission itself, one for the submitter, and a list of forms
    # for the authors

    empty_author_form = NameEmailForm(email_required=False)

    if request.method == 'POST':
        # get a backup submission now, the model form may change some
        # fields during validation
        prev_submission = Submission.objects.get(pk=submission.pk)

        edit_form = EditSubmissionForm(request.POST, instance=submission, prefix="edit")
        submitter_form = NameEmailForm(request.POST, prefix="submitter")
        replaces_form = ReplacesForm(request.POST,name=submission.name)
        author_forms = [ NameEmailForm(request.POST, email_required=False, prefix=prefix)
                         for prefix in request.POST.getlist("authors-prefix")
                         if prefix != "authors-" ]

        # trigger validation of all forms
        validations = [edit_form.is_valid(), submitter_form.is_valid(), replaces_form.is_valid()] + [ f.is_valid() for f in author_forms ]
        if all(validations):
            submission.submitter = submitter_form.cleaned_line()
            replaces = replaces_form.cleaned_data.get("replaces", [])
            submission.replaces = ",".join(o.name for o in replaces)
            submission.authors = "\n".join(f.cleaned_line() for f in author_forms)
            edit_form.save(commit=False) # transfer changes

            if submission.rev != prev_submission.rev:
                rename_submission_files(submission, prev_submission.rev, submission.rev)

            submission.state = DraftSubmissionStateName.objects.get(slug="manual")
            submission.save()

            send_manual_post_request(request, submission, errors)

            changed_fields = [
                submission._meta.get_field(f).verbose_name
                for f in list(edit_form.fields.keys()) + ["submitter", "authors"]
                if getattr(submission, f) != getattr(prev_submission, f)
            ]

            if changed_fields:
                desc = u"Edited %s and sent request for manual post" % u", ".join(changed_fields)
            else:
                desc = "Sent request for manual post"

            create_submission_event(request, submission, desc)

            return redirect("submit_submission_status", submission_id=submission.pk)
        else:
            form_errors = True
    else:
        edit_form = EditSubmissionForm(instance=submission, prefix="edit")
        submitter_form = NameEmailForm(initial=submission.submitter_parsed(), prefix="submitter")
        replaces_form = ReplacesForm(name=submission.name,initial=DocAlias.objects.filter(name__in=submission.replaces.split(",")))
        author_forms = [ NameEmailForm(initial=author, email_required=False, prefix="authors-%s" % i)
                         for i, author in enumerate(submission.authors_parsed()) ]

    return render(request, 'submit/edit_submission.html',
                              {'selected': 'status',
                               'submission': submission,
                               'edit_form': edit_form,
                               'submitter_form': submitter_form,
                               'replaces_form': replaces_form,
                               'author_forms': author_forms,
                               'empty_author_form': empty_author_form,
                               'errors': errors,
                               'form_errors': form_errors,
                              })


def confirm_submission(request, submission_id, auth_token):
    submission = get_object_or_404(Submission, pk=submission_id)

    key_matched = submission.auth_key and auth_token == generate_access_token(submission.auth_key)
    if not key_matched: key_matched = auth_token == submission.auth_key # backwards-compat

    if request.method == 'POST' and submission.state_id in ("auth", "aut-appr") and key_matched:
        submitter_parsed = submission.submitter_parsed()
        if submitter_parsed["name"] and submitter_parsed["email"]:
            # We know who approved it
            desc = "New version approved"
        elif submission.state_id == "auth":
            desc = "New version approved by author"
        else:
            desc = "New version approved by previous author"

        post_submission(request, submission, desc)

        create_submission_event(request, submission, "Confirmed and posted submission")

        return redirect("doc_view", name=submission.name)

    return render(request, 'submit/confirm_submission.html', {
        'submission': submission,
        'key_matched': key_matched,
    })


def approvals(request):
    approvals = approvable_submissions_for_user(request.user)
    preapprovals = preapprovals_for_user(request.user)

    days = 30
    recently_approved = recently_approved_by_user(request.user, datetime.date.today() - datetime.timedelta(days=days))

    return render(request, 'submit/approvals.html',
                              {'selected': 'approvals',
                               'approvals': approvals,
                               'preapprovals': preapprovals,
                               'recently_approved': recently_approved,
                               'days': days })


@role_required("Secretariat", "Area Director", "WG Chair", "RG Chair")
def add_preapproval(request):
    groups = Group.objects.filter(type__in=("wg", "rg")).exclude(state__in=["conclude","bof-conc"]).order_by("acronym").distinct()

    if not has_role(request.user, "Secretariat"):
        groups = groups.filter(role__person__user=request.user,role__name__in=['ad','chair','delegate','secr'])

    if request.method == "POST":
        form = PreapprovalForm(request.POST)
        form.groups = groups
        if form.is_valid():
            p = Preapproval()
            p.name = form.cleaned_data["name"]
            p.by = request.user.person
            p.save()

            return HttpResponseRedirect(urlreverse("submit_approvals") + "#preapprovals")
    else:
        form = PreapprovalForm()

    return render(request, 'submit/add_preapproval.html',
                              {'selected': 'approvals',
                               'groups': groups,
                               'form': form })

@role_required("Secretariat", "WG Chair", "RG Chair")
def cancel_preapproval(request, preapproval_id):
    preapproval = get_object_or_404(Preapproval, pk=preapproval_id)

    if preapproval not in preapprovals_for_user(request.user):
        raise HttpResponseForbidden("You do not have permission to cancel this preapproval.")

    if request.method == "POST" and request.POST.get("action", "") == "cancel":
        preapproval.delete()

        return HttpResponseRedirect(urlreverse("submit_approvals") + "#preapprovals")

    return render(request, 'submit/cancel_preapproval.html',
                              {'selected': 'approvals',
                               'preapproval': preapproval })


@role_required('Secretariat')
def manualpost(request):
    '''
    Main view for manual post requests
    '''

    manual = Submission.objects.filter(state_id = "manual").distinct()
    
    for s in manual:
        s.passes_checks = all([ c.passed!=False for c in s.checks.all() ])
        s.errors = validate_submission(s)

    awaiting_draft = Submission.objects.filter(state_id = "manual-awaiting-draft").distinct()

    return render(request, 'submit/manual_post.html',
                  {'manual': manual,
                   'awaiting_draft': awaiting_draft})

@role_required('Secretariat',)
def add_manualpost_email(request):
    """Add email to submission history"""

    if request.method == 'POST':
        button_text = request.POST.get('submit', '')
        if button_text == 'Cancel':
            return redirect("submit/manual_post.html")

        form = SubmissionEmailForm(request.POST)
        if form.is_valid():
            name = form.cleaned_data['name']
            message = form.cleaned_data['message']
            #in_reply_to = form.cleaned_data['in_reply_to']
            # create Message

            if form.cleaned_data['direction'] == 'incoming':
                msgtype = 'msgin'
            else:
                msgtype = 'msgout'

            add_submission_email(remote_ip=request.META.get('REMOTE_ADDR', None),
                                 name = name,
                                 message = message,
                                 by = request.user.person,
                                 msgtype = msgtype)
                                         
            messages.success(request, 'Email added.')
            return redirect("submit_manualpost_list")
    else:
        form = SubmissionEmailForm()

    return render(request, 'submit/add_submit_email.html',dict(form=form))


@role_required('Secretariat',)
def send_email(request, submission_id, message_id=None):
    """Send an email related to a submission"""
    submission = get_submission_or_404(submission_id, access_token = None)

    if request.method == 'POST':
        button_text = request.POST.get('submit', '')
        if button_text == 'Cancel':
            return redirect('submit_submission_emails_by_hash',
                            submission_id=submission.id,
                            access_token=submission.access_token())

        form = MessageModelForm(request.POST)
        if form.is_valid():
            # create Message
            msg = Message.objects.create(
                    by = request.user.person,
                    subject = form.cleaned_data['subject'],
                    frm = form.cleaned_data['frm'],
                    to = form.cleaned_data['to'],
                    cc = form.cleaned_data['cc'],
                    bcc = form.cleaned_data['bcc'],
                    reply_to = form.cleaned_data['reply_to'],
                    body = form.cleaned_data['body']
            )
            
            in_reply_to_id = form.cleaned_data['in_reply_to_id']
            in_reply_to = None
            
            if in_reply_to_id:
                try:
                    in_reply_to = Message.objects.get(id=in_reply_to_id)
                except Message.DoesNotExist:
                    log("Unable to retrieve in_reply_to message: %s" % in_reply_to_id)

            SubmissionEmail.objects.create(
                    submission = submission,
                    msgtype = 'msgout',
                    by = request.user.person,
                    message = msg,
                    in_reply_to = in_reply_to)

            # send email
            send_mail_message(None,msg)

            messages.success(request, 'Email sent.')
            return redirect('submit_submission_emails_by_hash', 
                            submission_id=submission.id,
                            access_token=submission.access_token())

    else:
        reply_to = get_reply_to()
        msg = None
        
        if not message_id:
            addrs = gather_address_lists('sub_confirmation_requested',submission=submission).as_strings(compact=False)
            to_email = addrs.to
            cc = addrs.cc
            subject = 'Regarding {}'.format(submission.name)
        else:
            try:
                msg = Message.objects.get(id=message_id)
                to_email = msg.frm
                cc = msg.cc
                subject = 'Re:{}'.format(msg.subject)
            except Message.DoesNotExist:
                to_email = None
                cc = None
                subject = 'Regarding {}'.format(submission.name)

        initial = {
            'to': to_email,
            'cc': cc,
            'frm': settings.IDSUBMIT_FROM_EMAIL,
            'subject': subject,
            'reply_to': reply_to,
        }
        
        if msg:
            initial['in_reply_to_id'] = msg.id
        
        form = MessageModelForm(initial=initial)

    return render(request, "submit/email.html",  {
        'submission': submission,
        'access_token': submission.access_token(),
        'form':form})


def manual_post_email_submissions(request):
    """ Provide a list of the submission objects for which we have 
        an email history
    """

    manual = Submission.objects.filter(state_id = "secr-submit").distinct()

    return render(request, 'submit/premanual_post_list.html',
                  {'manual': manual})
    

def submission_emails(request, submission_id, access_token=None):
    submission = get_submission_or_404(submission_id, access_token)

    is_secretariat = has_role(request.user, "Secretariat")
    is_chair = submission.group and submission.group.has_role(request.user, "chair")

    messages = SubmissionEmail.objects.filter(submission=submission)

    return render(request, 'submit/submission_emails.html',
                  {'submission': submission,
                   'messages': messages})

def submission_email(request, submission_id, message_id, access_token=None):
    submission = get_submission_or_404(submission_id, access_token)

    message = get_object_or_404(SubmissionEmail, pk=message_id)    
    attachments = message.submissionemailattachment_set.all()
    
    return render(request, 'submit/submission_email.html',
                  {'submission': submission,
                   'message': message,
                   'attachments': attachments})

def submission_email_attachment(request, submission_id, message_id, filename, access_token=None):
    submission = get_submission_or_404(submission_id, access_token)

    message = get_object_or_404(SubmissionEmail, pk=message_id)

    attach = get_object_or_404(SubmissionEmailAttachment, 
                               submission_email=message, 
                               filename=filename)
    
    body = attach.body.encode('utf-8')
    
    response = HttpResponse(body, content_type='text/plain')
    response['Content-Disposition'] = 'attachment; filename=%s' % attach.filename
    response['Content-Length'] = len(body)
    return response
    

def get_submission_or_404(submission_id, access_token=None):
    submission = get_object_or_404(Submission, pk=submission_id)

    key_matched = access_token and submission.access_token() == access_token
    if not key_matched: key_matched = submission.access_key == access_token # backwards-compat
    if access_token and not key_matched:
        raise Http404

    return submission
