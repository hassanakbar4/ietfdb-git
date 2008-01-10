# Copyright The IETF Trust 2007, All Rights Reserved

import re, os, glob, time
from datetime import datetime, date

from django.shortcuts import render_to_response as render, get_object_or_404
from django.template.loader import render_to_string
from django.db import connection
from django.core.exceptions import ObjectDoesNotExist as ExceptionDoesNotExist

from django.http import HttpResponseRedirect

from django.http import HttpResponse, HttpResponseNotFound, HttpResponsePermanentRedirect, HttpResponseServerError
#from django.db.models import Q
#from django.views.generic.list_detail import object_list
from django.views.generic.list_detail import object_detail
from django.conf import settings

from models import IdSubmissionDetail, AnnouncementTemplate, TempIdAuthors, IdApprovedDetail, IdDates
from ietf.idtracker.models import Acronym, IETFWG, InternetDraft, EmailAddress, IDAuthor, IDInternal, DocumentComment, PersonOrOrgInfo
from ietf.announcements.models import ScheduledAnnouncement
#from ietf.proceedings.models import Meeting, Switches
from ietf.idsubmit.forms import IDUploadForm, SubmitterForm
from ietf.idsubmit.models import STATUS_CODE, SUBMISSION_ENV
from ietf.utils.mail import send_mail_text

from django.core.mail import BadHeaderError

# function parse_meta_data
# This function extract filename, revision, abstract, title, and
# author's information from the passed I-D content

from ietf.idsubmit.parser.draft_parser import DraftParser

def file_upload(request):
 
    form = None
    if request.POST:

        post_data = request.POST.copy()
        post_data.update(request.FILES)

        form = IDUploadForm(post_data)
        # form = IDUploadForm(request.POST, request.FILES)
        if form.is_bound and form.is_valid():
            if not request.FILES['txt_file']['content-type'].startswith('text'):
                return render("idsubmit/error.html", {'error_msg':STATUS_CODE[101]})

            dp = DraftParser(form.get_content('txt_file'))
            dp.set_remote_ip(request.META.get('REMOTE_ADDR'))

            if dp.status_id:
                file_path = form.save(dp.filename, dp.revision)
                dp.set_file_type(form.file_ext_list)

                idinits_msg = dp.check_idnits(file_path)
                if type(idinits_msg).__name__=='dict':
                    if idinits_msg['error'] > 0:
                        idinits_result = True
                        dp.status_id = 203
                        dp._set_meta_data_errors('idinits', "<li>This document has " + str(idinits_msg['error']) + " idnits error(s)</li>")
                    else:
                        idinits_result = False
                else:
                    idinits_result = False

                meta_data = dp.get_meta_data_fields()

                list = IdSubmissionDetail(**meta_data)
                try:
                    submission_id=list.save()
                except AttributeError:
                    return  render("idsubmit/error.html", {'error_msg':"Data Saving Error"})

                current_date = date.today()
                # current_date = date(2007, 11, 30)
                current_hour = int(time.strftime("%H", time.localtime()))
                first_cut_off_date = IdDates.objects.get(id=1).id_date 
                second_cut_off_date = IdDates.objects.get(id=2).id_date 
                ietf_monday_date = IdDates.objects.get(id=3).id_date 
                id_date_var = { 'first_cut_off_date' : first_cut_off_date, 'second_cut_off_date' : second_cut_off_date, 'ietf_monday' : ietf_monday_date}

                if (current_date >= first_cut_off_date and current_date < second_cut_off_date):
                    if (current_date == first_cut_off_date and current_hour < 9):
                        id_date_var['date_check_err_msg'] = "first_second"
                        return render("idsubmit/error.html", id_date_var)
                    else: # No more 00 submission
                        id_date_var['form'] = IDUploadForm()
                        id_date_var['cutoff_msg'] = "first_second"
                        return render ("idsubmit/upload.html", id_date_var)
                elif current_date >= second_cut_off_date and current_date < ietf_monday_date:
                    if (current_date == second_cut_off_date and current_hour < 9):
                        id_date_var['form'] = IDUploadForm()
                        id_date_var['cutoff_msg'] = "second_ietf"
                        return render ("idsubmit/upload.html", id_date_var)
                    else: #complete shut down of tool
                        id_date_var['date_check_err_msg'] = "second_ietf"
                        return render("idsubmit/error.html", id_date_var)

                threshold_msg = dp.check_dos_threshold()
                if threshold_msg:
                    return render("idsubmit/error.html", {'error_msg':threshold_msg})

                if dp.get_group_id(dp.get_wg_id()).acronym_id == 1027:
                    return render("idsubmit/error.html", {'error_msg':'There is no Acronym id'})
                for file_name, file_info in request.FILES.items():
                    if re.match(r'^[a-z0-9-\.]+$', dp.filename):
                        if file_info['filename'][-4:].lower() not in form.file_names.values():
                            return render("idsubmit/error.html", {'error_msg':'not allowed file format'})
                    else:
                        err_msg = "Filename contains non alpha-numeric character"
                        return render("idsubmit/error.html", {'error_msg':err_msg})

                # revision check
                if IdSubmissionDetail.objects.filter(filename__exact=dp.filename, status_id__gt=0):
                    return render("idsubmit/error.html", {'error_msg':STATUS_CODE[103]})

                id = IdSubmissionDetail.objects.filter(filename=dp.filename, revision=dp.revision, status_id__range=(-2, 50))
                if id.count() > 0:
                    return render("idsubmit/error.html", {'error_msg':'this document is already in the phase of processing'})

                authors_info = dp.get_author_detailInfo(dp.get_authors_info(),submission_id)
                for author_dict in authors_info:
                    author = TempIdAuthors(**author_dict)
                    try:
                        author.save()
                    except AttributeError:
                        return  render("idsubmit/error.html", {'error_msg':"Authors Data Saving Error"})

            return render("idsubmit/validate.html",{'meta_data'        : meta_data,
                                                    'meta_data_errors' : dp.meta_data_errors,
                                                    'submission_id'    : submission_id,
                                                    'authors_info'     : authors_info,
                                                    'submitter_form'   : SubmitterForm(),
                                                    'idinits_result'   : idinits_result,
                                                    'staging_url'      : settings.STAGING_URL,
                                                    'test_data':''})
        else:
            return render("idsubmit/error.html", {'error_msg':'This is not valid data' + str(form.errors) })
            form = IDUploadForm()
    else:
        form = IDUploadForm()
    return render ("idsubmit/upload.html",{'form':form})

def adjust_form(request, submission_id_or_name):
    submission = IdSubmissionDetail.objects.get(submission_id=submission_id_or_name)
    warning_list = ['title', 'abstract', 'author', 'revision', 'filename', 'version', 'creation', 'group']
    meta_data_errors = {}
    for warning in warning_list:
        if re.search(warning, submission.warning_message.lower()):
            meta_data_errors[warning] = True
            print warning
        else:
            print warning + ' : No Match'

    return object_detail(request, queryset=IdSubmissionDetail.objects.all(),
                                  object_id=submission_id_or_name,
                                  template_name="idsubmit/adjust_screen.html",
                                  template_object_name='object',
                                  extra_context={'authors': TempIdAuthors.objects.filter(submission__exact=submission_id_or_name),
                                                 'submitter_form': SubmitterForm,
                                                 'staging_url':settings.STAGING_URL,
                                                 'meta_data_errors':meta_data_errors})

def draft_status(request, submission_id_or_name):

    submission = None
    if re.compile("^\d+$").findall(submission_id_or_name) : # if submission_id
        submission = get_object_or_404(IdSubmissionDetail, pk=submission_id_or_name)
    elif re.compile('(-\d\d\.?(txt)?|/)$').findall(submission_id_or_name) :
        # if submission name
        subm_name = re.sub('(-\d\d\.?(txt)?|/)$', '', submission_id_or_name)
        submissions = IdSubmissionDetail.objects.filter(filename__exact=subm_name)

        if submissions.count() > 0 :
            submission = submissions[0]
    else:
        return render("idsubmit/error.html",{'error_msg':"unknown file format"})

    if submission is None :
        return HttpResponseNotFound()

    return render(
        "idsubmit/draft_status.html",
        {
            'object': submission,
            'authors': TempIdAuthors.objects.filter(
                    submission__exact=submission.submission_id),
            'status_msg': STATUS_CODE[submission.status_id],
            'staging_url':settings.STAGING_URL
        }
    )

def manual_post(request):
    param = request.POST.copy()
    authors_first_name = request.POST.getlist('author_first_name')
    authors_last_name  = request.POST.getlist('author_last_name')
    authors_email      = request.POST.getlist('author_email')
    param['authors'] = []
    cnt = 0
    for email in authors_email:
        param['authors'].append( {'author_email': email,
                                  'author_first_name': authors_first_name[cnt],
                                  'author_last_name': authors_last_name[cnt]} )
        cnt = cnt + 1
    subject = 'Manual Posting Requested for ' + param['filename'] + '-' + param['revision']
    message = render_to_string("idsubmit/manual_post_email.html", {'meta_data':param})
    from_email = 'idsubmission@ietf.org'
    if subject and message and from_email:
        submitter = SubmitterForm(param)
        if submitter.is_bound and submitter.is_valid():
            try:
                submission = IdSubmissionDetail.objects.get(submission_id=param['submission_id'])
            except IdSubmissionDetail.DoesNotExist:
                return False

            if submitter.save(submission, param['comment_to_sec']):
                return HttpResponseRedirect('/idsubmit/status/' + param['submission_id'])
            else:
                return render("idsubmit/error.html",{'error_msg':"The submitter information is not properly saved"})

        try:
            send_mail_text(request, 'ygpark2@gmail.com', from_email, subject, message)
        except BadHeaderError:
            return render("idsubmit/error.html",{'error_msg':"Invalid header found."})

    else:
        return render("idsubmit/error.html",{'error_msg':"Make sure all fields are entered and valid."})

def trigger_auto_post(request):
    args = request.GET.copy()
    if args.has_key('submission_id'):
        submission_id = args['submission_id']
    else:
        render("idsubmit/error.html",{'error_msg':"submission_id is not found"})
    if args.has_key('fname') and len(args['fname']):
        fname = ['fname']
    else:
        return render("idsubmit/error.html",{'error_msg':"Submitter's First Name is not found"})
    if args.has_key('lname') and len(args['lname']): lname = args['lname']
    else: return render("idsubmit/error.html",{'error_msg':"Submitter's Last Name is not found"})
    if args.has_key('submitter_email') and len(args['submitter_email']): submitter_email = args['submitter_email']
    else: return render("idsubmit/error.html",{'error_msg':"Submitter's Email Address is not found"})
    msg = ''

    try:
        submission = IdSubmissionDetail.objects.get(submission_id=submission_id)
    except IdSubmissionDetail.DoesNotExist:
        return render("idsubmit/error.html",{'error_msg':"The problem to get the Submitter's information"})

    submitterForm = SubmitterForm(args)
    if submitterForm.is_bound and submitterForm.is_valid():
        submitter = submitterForm.save(submission)
        if submitter:
            authors = TempIdAuthors.objects.filter(submission=submission_id)
            msg += "<br>subid: %s <br>sub tag: %d <br>" % (submission_id, submitter.person_or_org_tag)
            msg += '<a href="/idsubmit/verify/%s/%s/">proceed submitter verification</a><br>' % (submission_id, submission.auth_key)
            return render("idsubmit/status.html",{'submission_q':submission, 'authors_q':authors, 'msg':msg,'staging_url':settings.STAGING_URL,'debug_mode':settings.DEBUG})

            # return HttpResponseRedirect('/idsubmit/status/' + args['submission_id'])
        else:
            return render("idsubmit/error.html",{'error_msg':"The submitter information is not properly saved"})

def sync_docs (request, submission) :
    # sync docs with remote server.
    command = "sh %(BASE_DIR)s/idsubmit/sync_docs.sh --staging_path=%(staging_path)s --target_path_web=%(target_path_web)s --target_path_ftp=%(target_path_ftp)s --revision=%(revision)s --filename=%(filename)s --is_development=%(is_development)s" % {
        "filename" : submission.filename,
        "revision": submission.revision,
        "staging_path" : settings.STAGING_PATH,
        "target_path_web" : settings.TARGET_PATH_WEB,
        "target_path_ftp" : settings.TARGET_PATH_FTP,

        "BASE_DIR" : settings.BASE_DIR,
        "is_development" : (settings.SERVER_MODE == "production") and "0" or "1",

    }

    try :
        os.system(command)
    except :
        return False

    # remove files.
    try :
        [os.remove(i) for i in glob.glob("%(staging_path)s/%(filename)s-%(revision)s.*" % values)]
    except :
        pass

    return True


MSG_BODY_SCHEDULED_ANNOUNCEMENT = """New version (-%(revision)s) has been submitted for %(filename)s-%(revision)s.txt.
http://www.ietf.org/internet-drafts/%(filename)s-%(revision)s.txt
%(msg)s

IETF Secretariat.
"""

MSG_VERIFICATION = """A new version of I-D, %(filename)s-%(revision)s.txt has been successfuly submitted by %(submitter_name)s and posted to the IETF repository.

Filename:\t %(filename)s
Revision:\t %(revision)s
Title:\t\t %(title)s
Creation_date:\t %(creation_date)s
WG ID:\t\t %(group_name)s
Number_of_pages: %(txt_page_count)s

Abstract:
%(abstract)s

%(comment_to_sec)s

The IETF Secretariat.
"""

def verify_key(request, submission_id, auth_key, from_wg_or_sec=None):
    announcement_template = get_object_or_404(AnnouncementTemplate)

    subm = get_object_or_404(IdSubmissionDetail, pk=submission_id)

    now = datetime.now()

    if subm.auth_key != auth_key : # check 'auth_key'
        return HttpResponseNotFound(content="Auth Key Not Found.")

    if subm.status_id not in (4, 11, ) :
        # return status value 107, "Error - Draft is not in an appropriate
        # status for the requested page"
        return HttpResponseNotFound(content=STATUS_CODE[107])

    if subm.sub_email_priority is None :
        subm.sub_email_priority = 1

    approved_status = None
    if subm.filename is not None :
        try :
            approved_status = IdApprovedDetail.objects.get(filename=subm.filename).approved_status
        except ExceptionDoesNotExist :
            pass

    if approved_status == 1 or subm.revision != "00" or subm.group_id == 1027 :
        # populate table

        if subm.revision == "00" :
            # if the draft file alreay existed, error will be occured.
            if InternetDraft.objects.filter(filename__exact=subm.filename).count() > 0 :
                return HttpResponseServerError()

            internet_draft = InternetDraft(
                title=subm.title,
                id_document_key=subm.title.upper(),
                group=subm.group,
                filename=subm.filename,
                revision=subm.revision,
                revision_date=subm.submission_date,
                file_type=subm.file_type,
                txt_page_count=subm.txt_page_count,
                abstract=subm.abstract,
                status_id=1,
                intended_status_id=8,
                start_date=now,
                last_modified_date=now,
                review_by_rfc_editor=False,
                expired_tombstone=False,
            )

            internet_draft.save()

        # get the id_document_tag what was just created for the new
        # recorde
        else : # Existing version; update the existing record using new values
            try :
                internet_draft = InternetDraft.objects.get(filename=subm.filename)
            except ExceptionDoesNotExist :
                return HttpResponseServerError()
            else :
                try :
                    IDAuthor.objects.filter(document=internet_draft).delete()
                    EmailAddress.objects.filter(priority=internet_draft.id_document_tag).delete()
                except :
                    return HttpResponseServerError()

        authors_names = list()
        for author_info in TempIdAuthors.objects.filter(submission=subm) :
            email_address = EmailAddress.objects.filter(address=author_info.email_address)
            if email_address.count() > 0 :
                person_or_org_tag = email_address[0].person_or_org
            else :
                person_or_org_tag = PersonOrOrgInfo(
                    first_name=author_info.first_name,
                    last_name=author_info.last_name,
                    date_modified=now,
                )
                person_or_org_tag.save()

                EmailAddress(
                    person_or_org=person_or_org_tag,
                    type="Primary",
                    priority=1
                ).save()

            IDAuthor(
                document=internet_draft,
                person=person_or_org_tag,
            ).save()

            EmailAddress(
                person_or_org=person_or_org_tag,
                type="I-D",
                priority=internet_draft.id_document_tag
            ).save()

            # gathering author's names
            authors_names.append("%s. %s" % (author_info.first_name, author_info.last_name))

        subm.status_id = 7

        #################################################
        # Schedule I-D Announcement:
        # <Please read auto_post.cgi, sub schedule_id_announcement>
        cc_val = ""
        wgMail = str()
        # if group_acronym_id is 'Individual Submissions'
        if subm.group_id != 1027 :
            #subm.group.name
            cc_val = IETFWG.objects.get(pk=subm.group_id).email_address
            wgMail = "\nThis draft is a work item of the %(group_name)s Working Group of the IETF.\n" % {"group_name" : subm.group.name}

        body = announcement_template.id_action_announcement.replace("^^^", "\t"
        ).replace("##id_document_name##", subm.title
        ).replace("##authors##",    ", ".join(authors_names)
        ).replace("##filename##",       subm.filename
        ).replace("##revision##",       subm.revision
        ).replace("##txt_page_count##", str(subm.txt_page_count)
        ).replace("##revision_date##",  str(subm.submission_date)
        ).replace("##current_date##",   now.strftime("%F")
        ).replace("##current_time##",   now.strftime("%T")
        ).replace("##abstract##",       subm.abstract
        ).replace("##wgMail##",     wgMail
        )

        scheduled_announcement = ScheduledAnnouncement(
            mail_sent =    False,
            scheduled_by =     "IDST",
            to_be_sent_date =  now,
            to_be_sent_time =  "00:00",
            scheduled_date =   now,
            scheduled_time =   now,
            subject =      "I-D Action:$filename-$revision.txt",
            to_val =       "i-d-announce@ietf.org",
            from_val =     "Internet-Drafts@ietf.org",
            cc_val =       cc_val,
            body =         body,
            content_type =     "Multipart/Mixed; Boundary=\"NextPart\"",
        ).save()

        subm.status_id = 8

        temp_id_document_tag = InternetDraft.objects.get(filename=subm.filename).id_document_tag

        if IDInternal.objects.filter(draft=temp_id_document_tag).filter(rfc_flag=0).extra(where=["cur_state < 100", ]).count() > 0 :
            #################################################
            # Schedule New Version Notification:
            # <Please read auto_post.cgi, sub
            # schedule_new_version_notification>

            # Add comment to ID Tracker
            document_comments = DocumentComment(
                document_id =  temp_id_document_tag,
                rfc_flag =     0,
                public_flag =  1,
                date = now,
                time = now,
                version =      subm.revision,
                comment_text = "New version available",
            ).save()

            id_internal = IDInternal.objects.filter(draft=temp_id_document_tag).filter(rfc_flag=0)[0]
            msg = "Sub state has been changed to AD Follow up from New Id Needed"
            if id_internal.cur_sub_state_id == 5 :
                document_comments = DocumentComment(
                    document_id =  temp_id_document_tag,
                    rfc_flag =     0,
                    public_flag =  1,
                    date = now,
                    time = now,
                    version =      subm.revision,
                    comment_text = msg,
                ).save()

                id_internal.cur_sub_state_id = 2
                id_internal.prev_sub_state_id = 5
                id_internal.save()

            kwargs = subm.__dict__.copy()
            kwargs.update({"msg" : msg, })
            kwargs.update({"temp_id_document_tag" : temp_id_document_tag, })

            body = MSG_BODY_SCHEDULED_ANNOUNCEMENT % kwargs

            send_to = list()
            send_to.append(id_internal.state_change_notice_to)

            cursor = connection.cursor()
            # Django model does not handle the complex join query well, so use this.
            cursor.execute("select email_address from email_addresses a, id_internal b, iesg_login c where b.id_document_tag=%(temp_id_document_tag)s and rfc_flag=0 and b.job_owner=c.id and c.person_or_org_tag = a.person_or_org_tag and a.email_priority=1" % kwargs)
            __email_address = cursor.fetchone()
            if __email_address is not None and __email_address[0] not in send_to :
                send_to.append(__email_address[0])

            cursor.execute("select email_address from email_addresses a, ballots b, id_internal c,iesg_login d where c.id_document_tag=%(temp_id_document_tag)s and c.ballot_id=b.ballot_id and b.ad_id=d.id and d.person_or_org_tag=a.person_or_org_tag and a.email_priority=1 and b.discuss =1 and d.user_level=1" % kwargs)

            while True :
                __email_address = cursor.fetchone()
                if __email_address is None :
                    break
                if __email_address[0] in send_to :
                    continue

                send_to.append(__email_address[0])

            scheduled_announcement = ScheduledAnnouncement(
                mail_sent = False,
                scheduled_by =     "IDST",
                to_be_sent_date =  now,
                to_be_sent_time =  "00:00",
                scheduled_date =   now,
                scheduled_time =   now,
                subject =      "New Version Notification - %(filename)s-%(revision)s.txt" % kwargs,
                to_val =       ",".join([str(eb) for eb in send_to if eb is not None]),
                from_val =     "Internet-Drafts@ietf.org",
                cc_val =       cc_val,
                body =         body,
            ).save()

            subm.status_id = 9

            #################################################
            # Copy Document(s) to production servers:
            # <Please read auto_post.cgi, sub sync_docs>
            try :
                sync_docs(request, subm)
            except OSError :
                return HttpResponseServerError()

            subm.status_id = -1

            # Notify All Authors:
            # <Please read auto_post.cgi, sub notify_all_authors>

            cc_email = list()
            if subm.group_id == 1027 :
                group_acronym = "Independent Submission"
            else :
                group_acronym = subm.group.name
                #cc_email.append(IETFWG.objects.get(group_acronym=subm.group).email_address)

            subm.comment_to_sec = subm.comment_to_sec and "\nComment:\n%s" % subm.comment_to_sec or ""

            try :
                (submitter_name, submitter_email, ) = subm.submitter.email()
            except :
                # for debuggin in development mode.
                if settings.SERVER_MODE == "production" :
                    raise
                else :
                    submitter_name = ""
                    submitter_email = ""

            for author_info in TempIdAuthors.objects.filter(submission=subm) :
                if not author_info.email_address.strip() and submitter_email == author_info.email_address :
                    continue

                if author_info.email_address not in cc_email :
                    cc_email.append(author_info.email_address)

            to_email = submitter_email
            kwargs.update(
                {
                    "group_name" : subm.group.name,
                    "submitter_name" : submitter_name,
                }
            )
            send_mail_text(
                request,
                to_email,
                "IETF I-D Submission Tool <idsubmission@ietf.org>",
                "New Version Notification for %(filename)s-%(revision)s" % kwargs,
                MSG_VERIFICATION % kwargs,
                cc_email,
            )

        subm.save()

        if from_wg_or_sec == "wg" :
            return HttpResponsePermanentRedirect("https://datatracker.ietf.org/cgi-bin/wg/wg_init_rev_approval.cgi?from_auto_post=1&submission_id=%s" % (subm.submission_id, ))
        elif from_wg_or_sec == "sec" :
            return HttpResponsePermanentRedirect("https://datatracker.ietf.org/cgi-bin/secretariat/init_rev_approval.cgi?from_auto_post=1&submission_id=%s" % (subm.submission_id, ))
        else : # redirect to /idsubmit/status/<filename>
            return HttpResponsePermanentRedirect("/idsubmit/status/%s" % (subm.filename, ))

    else :
        # set the status_id to 10
        subm.status_id = 10

        # get submitter's name and email address
        (submitter_name, submitter_email, ) = subm.submitter.email()

        # get acronym from acronym where acronym_id=group_acronym_id
        # get id_approval_request_msg from announcement_template
        id_approval_request_msg = announcement_template.id_approval_request_msg.replace("##submitter_name##", submitter_name).replace("##submitter_email##", submitter_email).replace("##filename##", subm.filename)
        # send a message to '<acronym>-chairs@tools.ietf.org' from 'IETF
        # I-D Submission Tool <idst-developers@ietf.org>,
        # subject:Initial Version Approval Request or <filename>

        send_mail_text(
            request,
            "%s-chairs@tools.ietf.org" % (str(subm.group), ),
            "IETF I-D Submission Tool <idst-developers@ietf.org>",
            "Initial Version Approval Request or %s" % (subm.filename, ),
            id_approval_request_msg
        )

        subm.save()

        # redirect the page to /idsubmit/status/<filename>
        return HttpResponsePermanentRedirect("/idsubmit/status/%s" % (subm.filename, ))

MSG_CANCEL = """This message is to notify you that submission of an Internet-Draft, %(filename)s-%(revision)s, has just been cancelled by a user whose computer has an IP address of %(remote_ip)s.

The IETF Secretariat.
"""
SUBJECT_CANCEL = "Submission of %(filename)s-%(revision)s has been Cancelled"
FROM_EMAIL_CANCEL = "IETF I-D Submission Tool <idsubmission@ietf.org>"

def cancel_draft (request, submission_id) :
    """
    This view was ported from the cancel routine in
    'ietf/branch/legacy/idsubmit/status.cgi'.

    NOTE: The below commented parts will be removed after all the codes is verified.
    """

    # get submission
    submission = get_object_or_404(IdSubmissionDetail, pk=submission_id)

    # rename the submitted document to new name with canceled tag.
    path_orig_sub = os.path.join(
        settings.STAGING_PATH,
        "%s-%s" % (submission.filename, submission.revision, ),
    )
    path_orig = os.path.join(
        settings.STAGING_PATH,
        "%s-%s.txt" % (submission.filename, submission.revision, ),
    )
    path_cancelled = os.path.join(
        settings.STAGING_PATH,
        "%s-%s-%s-cancelled.txt" % (submission.filename, submission.revision, submission.submission_id, ),
    )
    os.rename(path_orig, path_cancelled)

    # remove all sub document.
    for i in glob.glob("%s*" % path_orig_sub) :
        os.remove(i)

    # to notify 'cancel' to the submitter.
    if submission.status_id > -3 and submission.status_id < 100 :
        to_email = [i.email_address for i in TempIdAuthors.objects.filter(submission=submission) if i.email_address.strip()]

        kwargs = submission.__dict__.copy()
        kwargs.update(
            {
                "remote_ip" : request.META.get("REMOTE_ADDR")
            }
        )

        send_mail_text(
            request,
            to_email,
            FROM_EMAIL_CANCEL,
            SUBJECT_CANCEL % kwargs,
            MSG_CANCEL % kwargs,
        )

    # >> db_update($dbh,"update id_submission_detail set status_id=-4 where submission_id=$sub_id");
    # if everything is OK, change the status_id to -4
    submission.status_id = -4
    submission.save()

    return render(
        "idsubmit/draft_status.html",
        {
            'object': submission,
            'authors': TempIdAuthors.objects.filter(
                    submission__exact=submission.submission_id),
            'status_msg': STATUS_CODE[submission.status_id],
            'staging_url':settings.STAGING_URL
        }
    )


