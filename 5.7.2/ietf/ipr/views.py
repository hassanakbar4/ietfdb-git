# Copyright The IETF Trust 2007, All Rights Reserved

import datetime
import itertools

from django.conf import settings
from django.contrib import messages
from django.core.urlresolvers import reverse as urlreverse
from django.db.models import Q
from django.forms.models import inlineformset_factory
from django.forms.formsets import formset_factory
from django.http import HttpResponse, Http404, HttpResponseRedirect
from django.shortcuts import render_to_response as render, get_object_or_404, redirect
from django.template import RequestContext
from django.template.loader import render_to_string

from ietf.doc.models import DocAlias
from ietf.group.models import Role
from ietf.ietfauth.utils import role_required, has_role
from ietf.ipr.mail import message_from_message, get_reply_to
from ietf.ipr.fields import tokeninput_id_name_json
from ietf.ipr.forms import (HolderIprDisclosureForm, GenericDisclosureForm,
    ThirdPartyIprDisclosureForm, DraftForm, RfcForm, SearchForm, MessageModelForm,
    AddCommentForm, AddEmailForm, NotifyForm, StateForm, NonDocSpecificIprDisclosureForm,
    GenericIprDisclosureForm)
from ietf.ipr.models import (IprDisclosureStateName, IprDisclosureBase,
    HolderIprDisclosure, GenericIprDisclosure, ThirdPartyIprDisclosure,
    NonDocSpecificIprDisclosure, IprDocRel,
    RelatedIpr,IprEvent)
from ietf.ipr.utils import iprs_from_docs, related_docs
from ietf.message.models import Message
from ietf.message.utils import infer_message
from ietf.person.models import Person
from ietf.secr.utils.document import get_rfc_num, is_draft
from ietf.utils.draft_search import normalize_draftname
from ietf.utils.mail import send_mail, send_mail_message

# ----------------------------------------------------------------
# Globals
# ----------------------------------------------------------------
# maps string type or ipr model class to corresponding edit form
ipr_form_mapping = { 'specific':HolderIprDisclosureForm,
                     'generic':GenericDisclosureForm,
                     'third-party':ThirdPartyIprDisclosureForm,
                     'HolderIprDisclosure':HolderIprDisclosureForm,
                     'GenericIprDisclosure':GenericIprDisclosureForm,
                     'ThirdPartyIprDisclosure':ThirdPartyIprDisclosureForm,
                     'NonDocSpecificIprDisclosure':NonDocSpecificIprDisclosureForm }

class_to_type = { 'HolderIprDisclosure':'specific',
                  'GenericIprDisclosure':'generic',
                  'ThirdPartyIprDisclosure':'third-party',
                  'NonDocSpecificIprDisclosure':'generic' }
# ----------------------------------------------------------------
# Helper Functions
# ----------------------------------------------------------------
def get_genitive(name):
    """Return the genitive form of name"""
    return name + "'" if name.endswith('s') else name + "'s"

def get_ipr_summary(disclosure):
    """Return IPR related document names as a string"""
    ipr = []
    for doc in disclosure.docs.all():
        if doc.name.startswith('rfc'):
            ipr.append('RFC {}'.format(doc.name[3:]))
        else:
            ipr.append(doc.name)
    
    if disclosure.other_designations:
        ipr.append(disclosure.other_designations)

    if len(ipr) == 1:
        ipr = ipr[0]
    elif len(ipr) == 2:
        ipr = " and ".join(ipr)
    elif len(ipr) > 2:
        ipr = ", ".join(ipr[:-1]) + ", and " + ipr[-1]

    return ipr

def get_pseudo_submitter(ipr):
    """Returns a tuple (name, email) contact for this disclosure.  Order of preference
    is submitter, ietfer, holder (per legacy app)"""
    name = 'UNKNOWN NAME - NEED ASSISTANCE HERE'
    email = 'UNKNOWN EMAIL - NEED ASSISTANCE HERE'
    if ipr.submitter_email:
        name = ipr.submitter_name
        email = ipr.submitter_email
    elif hasattr(ipr, 'ietfer_contact_email') and ipr.ietfer_contact_email:
        name = ipr.ietfer_name
        email = ipr.ietfer_contact_email
    elif hasattr(ipr, 'holder_contact_email') and ipr.holder_contact_email:
        name = ipr.holder_contact_name
        email = ipr.holder_contact_email
    
    return (name,email)

def get_document_emails(ipr):
    """Returns a list of messages to inform document authors that a new IPR disclosure
    has been posted"""
    messages = []
    for rel in ipr.iprdocrel_set.all():
        doc = rel.document.document
        authors = doc.authors.all()
        
        if is_draft(doc):
            doc_info = 'Internet-Draft entitled "{}" ({})'.format(doc.title,doc.name)
        else:
            doc_info = 'RFC entitled "{}" (RFC{})'.format(doc.title,get_rfc_num(doc))
            
        # build cc list
        if doc.group.acronym == 'none':
            if doc.ad and is_draft(doc):
                cc_list = doc.ad.role_email('ad').address
            else:
                role = Role.objects.filter(group__acronym='gen',name='ad')[0]
                cc_list = role.email.address

        else:
            cc_list = get_wg_email_list(doc.group)

        author_emails = ','.join([a.address for a in authors])
        author_names = ', '.join([a.person.name for a in authors])
        cc_list += ", ipr-announce@ietf.org"
    
        context = dict(
            doc_info=doc_info,
            to_email=author_emails,
            to_name=author_names,
            cc_email=cc_list,
            ipr=ipr)
        text = render_to_string('ipr/posted_document_email.txt',context)
        messages.append(text)
    
    return messages

def get_posted_emails(ipr):
    """Return a list of messages suitable to initialize a NotifyFormset for
    the notify view when a new disclosure is posted"""
    messages = []
    # NOTE 1000+ legacy iprs have no submitter_email
    # add submitter message
    if True:
        context = dict(
            to_email=ipr.submitter_email,
            to_name=ipr.submitter_name,
            cc_email=get_update_cc_addrs(ipr),
            ipr=ipr)
        text = render_to_string('ipr/posted_submitter_email.txt',context)
        messages.append(text)
    
    # add email to related document authors / parties
    if ipr.iprdocrel_set.all():
        messages.extend(get_document_emails(ipr))
    
    # if Generic disclosure add message for General Area AD
    if ipr.get_classname() in ('GenericIprDisclosure','NonDocSpecificIprDisclosure'):
        role = Role.objects.filter(group__acronym='gen',name='ad').first()
        context = dict(
            to_email=role.email.address,
            to_name=role.person.name,
            ipr=ipr)
        text = render_to_string('ipr/posted_generic_email.txt',context)
        messages.append(text)
        
    return messages

def get_update_submitter_emails(ipr):
    """Returns list of messages, as flat strings, to submitters of IPR(s) being
    updated"""
    messages = []
    email_to_iprs = {}
    email_to_name = {}
    for related in ipr.updates:
        name, email = get_pseudo_submitter(related.target)
        email_to_name[email] = name
        if email in email_to_iprs:
            email_to_iprs[email].append(related.target)
        else:
            email_to_iprs[email] = [related.target]
        
    for email in email_to_iprs:
        context = dict(
            to_email=email,
            to_name=email_to_name[email],
            iprs=email_to_iprs[email],
            new_ipr=ipr,
            reply_to=get_reply_to())
        text = render_to_string('ipr/update_submitter_email.txt',context)
        messages.append(text)
    return messages
    
def get_holders(ipr):
    """Recursive function to follow chain of disclosure updates and return holder emails"""
    items = []
    for x in [ y.target.get_child() for y in ipr.updates]:
        items.extend(get_holders(x))
    return [ipr.holder_contact_email] + items

def get_update_cc_addrs(ipr):
    """Returns list (as a string) of email addresses to use in CC: for an IPR update.
    Logic is from legacy tool.  Append submitter or ietfer email of first-order updated
    IPR, append holder of updated IPR, follow chain of updates, appending holder emails
    """
    emails = []
    if not ipr.updates:
        return ''
    for rel in ipr.updates:
        if rel.target.submitter_email:
            emails.append(rel.target.submitter_email)
        elif hasattr(rel.target,'ietfer_email') and rel.target.ietfer_email:
            emails.append(rel.target.ietfer_email)
    emails = emails + get_holders(ipr)
    
    return ','.join(list(set(emails)))

def get_wg_email_list(group):
    """Returns a string of comman separated email addresses for the Area Directors and WG Chairs
    """
    result = []
    roles = itertools.chain(Role.objects.filter(group=group.parent,name='ad'),
                            Role.objects.filter(group=group,name='chair'))
    for role in roles:
        result.append(role.email.address)

    if group.list_email:
        result.append(group.list_email)

    return ', '.join(result)

def set_disclosure_title(disclosure):
    """Set the title of the disclosure"""

    if disclosure.get_classname() == 'HolderIprDisclosure':
        ipr_summary = get_ipr_summary(disclosure)
        title = get_genitive(disclosure.holder_legal_name) + ' Statement about IPR related to {}'.format(ipr_summary)
    elif disclosure.get_classname() in ('GenericIprDisclosure','NonDocSpecificIprDisclosure'):
        title = get_genitive(disclosure.holder_legal_name) + ' General License Statement'
    elif disclosure.get_classname() == 'ThirdPartyIprDisclosure':
        ipr_summary = get_ipr_summary(disclosure)
        title = get_genitive(disclosure.ietfer_name) + ' Statement about IPR related to {} belonging to {}'.format(ipr_summary,disclosure.holder_legal_name)
    
    # truncate for db
    if len(title) > 255:
        title = title[:252] + "..."
    disclosure.title = title

# ----------------------------------------------------------------
# Ajax Views
# ----------------------------------------------------------------
def ajax_search(request):
    q = [w.strip() for w in request.GET.get('q', '').split() if w.strip()]

    if not q:
        objs = IprDisclosureBase.objects.none()
    else:
        query = Q()
        for t in q:
            query &= Q(title__icontains=t)

        objs = IprDisclosureBase.objects.filter(query)

    objs = objs.distinct()[:10]

    return HttpResponse(tokeninput_id_name_json(objs), content_type='application/json')
    
def ajax_draft_search(request):
    q = [w.strip() for w in request.GET.get('q', '').split() if w.strip()]

    if not q:
        objs = DocAlias.objects.none()
    else:
        query = Q()
        for t in q:
            query &= Q(name__icontains=t)

        objs = DocAlias.objects.filter(name__startswith='draft').filter(query)

    objs = objs.distinct()[:10]

    return HttpResponse(tokeninput_id_name_json(objs), content_type='application/json')

def ajax_rfc_search(request):
    # expects one numeric term
    q = [w.strip() for w in request.GET.get('q', '').split() if w.strip()]

    if not q:
        objs = DocAlias.objects.none()
    else:
        query = Q()
        query &= Q(name__startswith='rfc%s' % q[0])

        objs = DocAlias.objects.filter(query)

    objs = objs.distinct()[:10]

    return HttpResponse(tokeninput_id_name_json(objs), content_type='application/json')
    
# ----------------------------------------------------------------
# Views
# ----------------------------------------------------------------
def about(request):
    return render("ipr/disclosure.html", {}, context_instance=RequestContext(request))

@role_required('Secretariat',)
def add_comment(request, id):
    """Add comment to disclosure history"""
    ipr = get_object_or_404(IprDisclosureBase, id=id)
    login = request.user.person

    if request.method == 'POST':
        form = AddCommentForm(request.POST)
        if form.is_valid():
            if form.cleaned_data.get('private'):
                type_id = 'private_comment'
            else:
                type_id = 'comment'
                
            IprEvent.objects.create(
                by=login,
                type_id=type_id,
                disclosure=ipr,
                desc=form.cleaned_data['comment']
            )
            messages.success(request, 'Comment added.')
            return redirect("ipr_history", id=ipr.id)
    else:
        form = AddCommentForm()
  
    return render('ipr/add_comment.html',dict(ipr=ipr,form=form),
        context_instance=RequestContext(request))

@role_required('Secretariat',)
def add_email(request, id):
    """Add email to disclosure history"""
    ipr = get_object_or_404(IprDisclosureBase, id=id)
    
    if request.method == 'POST':
        button_text = request.POST.get('submit', '')
        if button_text == 'Cancel':
            return redirect("ipr_history", id=ipr.id)
        
        form = AddEmailForm(request.POST,ipr=ipr)
        if form.is_valid():
            message = form.cleaned_data['message']
            in_reply_to = form.cleaned_data['in_reply_to']
            # create Message
            msg = message_from_message(message,request.user.person)
            
            # create IprEvent
            if form.cleaned_data['direction'] == 'incoming':
                type_id = 'msgin'
            else:
                type_id = 'msgout'
            IprEvent.objects.create(
                type_id = type_id,
                by = request.user.person,
                disclosure = ipr,
                message = msg,
                in_reply_to = in_reply_to
            )
            messages.success(request, 'Email added.')
            return redirect("ipr_history", id=ipr.id)
    else:
        form = AddEmailForm(ipr=ipr)
        
    return render('ipr/add_email.html',dict(ipr=ipr,form=form),
        context_instance=RequestContext(request))
        
@role_required('Secretariat',)
def admin(request,state):
    """Administrative disclosure listing.  For non-posted disclosures"""
    if state == 'removed':
        states = ('removed','rejected')
    else:
        states = [state]
    iprs = IprDisclosureBase.objects.filter(state__in=states).order_by('-time')
    
    tabs = [('Pending','pending',urlreverse('ipr_admin',kwargs={'state':'pending'}),True),
        ('Removed','removed',urlreverse('ipr_admin',kwargs={'state':'removed'}),True),
        ('Parked','parked',urlreverse('ipr_admin',kwargs={'state':'parked'}),True)]
    
    template = 'ipr/admin_' + state + '.html'
    return render(template,  {
        'iprs': iprs,
        'tabs': tabs,
        'selected': state},
        context_instance=RequestContext(request)
    )

@role_required('Secretariat',)
def edit(request, id, updates=None):
    """Secretariat only edit disclosure view"""
    ipr = get_object_or_404(IprDisclosureBase, id=id).get_child()
    type = class_to_type[ipr.get_classname()]
    
    # only include extra when initial formset is empty
    if ipr.iprdocrel_set.filter(document__name__startswith='draft'):
        draft_extra = 0
    else:
        draft_extra = 1
    if ipr.iprdocrel_set.filter(document__name__startswith='rfc'):
        rfc_extra = 0
    else:
        rfc_extra = 1
    DraftFormset = inlineformset_factory(IprDisclosureBase, IprDocRel, form=DraftForm, can_delete=True, extra=draft_extra)
    RfcFormset = inlineformset_factory(IprDisclosureBase, IprDocRel, form=RfcForm, can_delete=True, extra=rfc_extra)

    if request.method == 'POST':
        form = ipr_form_mapping[ipr.get_classname()](request.POST,instance=ipr)
        if not type == 'generic':
            draft_formset = DraftFormset(request.POST, instance=ipr, prefix='draft')
            rfc_formset = RfcFormset(request.POST, instance=ipr, prefix='rfc')
        else:
            draft_formset = None
            rfc_formset = None
            
        if request.user.is_anonymous():
            person = Person.objects.get(name="(System)")
        else:
            person = request.user.person
            
        # check formset validity
        if not type == 'generic':
            valid_formsets = draft_formset.is_valid() and rfc_formset.is_valid()
        else:
            valid_formsets = True
            
        if form.is_valid() and valid_formsets: 
            updates = form.cleaned_data.get('updates')
            disclosure = form.save(commit=False)
            disclosure.save()
            
            if not type == 'generic':
                # clear and recreate IprDocRels
                # IprDocRel.objects.filter(disclosure=ipr).delete()
                draft_formset = DraftFormset(request.POST, instance=disclosure, prefix='draft')
                draft_formset.save()
                rfc_formset = RfcFormset(request.POST, instance=disclosure, prefix='rfc')
                rfc_formset.save()

            set_disclosure_title(disclosure)
            disclosure.save()
            
            # clear and recreate IPR relationships
            RelatedIpr.objects.filter(source=ipr).delete()
            if updates:
                for target in updates:
                    RelatedIpr.objects.create(source=disclosure,target=target,relationship_id='updates')
                
            # create IprEvent
            IprEvent.objects.create(
                type_id='changed_disclosure',
                by=person,
                disclosure=disclosure,
                desc="Changed disclosure metadata")
            
            messages.success(request,'Disclosure modified')
            return redirect("ipr_show", id=ipr.id)
        
        else:
            # assert False, form.errors
            pass
    else:
        if ipr.updates:
            form = ipr_form_mapping[ipr.get_classname()](instance=ipr,initial={'updates':[ x.target for x in ipr.updates ]})
        else:
            form = ipr_form_mapping[ipr.get_classname()](instance=ipr)
        #disclosure = IprDisclosureBase()    # dummy disclosure for inlineformset
        dqs=IprDocRel.objects.filter(document__name__startswith='draft')
        rqs=IprDocRel.objects.filter(document__name__startswith='rfc')
        draft_formset = DraftFormset(instance=ipr, prefix='draft',queryset=dqs)
        rfc_formset = RfcFormset(instance=ipr, prefix='rfc',queryset=rqs)
        
    return render("ipr/details_edit.html",  {
        'form': form,
        'draft_formset':draft_formset,
        'rfc_formset':rfc_formset,
        'type':type},
        context_instance=RequestContext(request)
    )

@role_required('Secretariat',)
def email(request, id):
    """Send an email regarding this disclosure"""
    ipr = get_object_or_404(IprDisclosureBase, id=id).get_child()
    
    if request.method == 'POST':
        button_text = request.POST.get('submit', '')
        if button_text == 'Cancel':
            return redirect("ipr_show", id=ipr.id)
            
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

            # create IprEvent
            IprEvent.objects.create(
                type_id = 'msgout',
                by = request.user.person,
                disclosure = ipr,
                response_due = form.cleaned_data['response_due'],
                message = msg,
            )

            # send email
            send_mail_message(None,msg)

            messages.success(request, 'Email sent.')
            return redirect('ipr_show', id=ipr.id)
    
    else:
        reply_to = get_reply_to()
        initial = { 
            'to': ipr.submitter_email,
            'frm': settings.IPR_EMAIL_TO,
            'subject': 'Regarding {}'.format(ipr.title),
            'reply_to': reply_to,
        }
        form = MessageModelForm(initial=initial)
    
    return render("ipr/email.html",  {
        'ipr': ipr,
        'form':form},
        context_instance=RequestContext(request)
    )
    
def history(request, id):
    """Show the history for a specific IPR disclosure"""
    ipr = get_object_or_404(IprDisclosureBase, id=id).get_child()
    events = ipr.iprevent_set.all().order_by("-time", "-id").select_related("by")
    if not has_role(request.user, "Secretariat"):
        events = events.exclude(type='private_comment')
        
    tabs = [('Disclosure','disclosure',urlreverse('ipr_show',kwargs={'id':id}),True),
            ('History','history',urlreverse('ipr_history',kwargs={'id':id}),True)]

    return render("ipr/details_history.html",  {
        'events':events,
        'ipr': ipr,
        'tabs':tabs,
        'selected':'history'},
        context_instance=RequestContext(request)
    )

def iprs_for_drafts_txt(request):
    docipr = {}

    for o in IprDocRel.objects.filter(disclosure__state='posted').select_related('document'):
        name = o.document.name
        if name.startswith("rfc"):
            name = name.upper()

        if not name in docipr:
            docipr[name] = []

        docipr[name].append(o.disclosure_id)

    lines = [ u"# Machine-readable list of IPR disclosures by draft name" ]
    for name, iprs in docipr.iteritems():
        lines.append(name + "\t" + "\t".join(unicode(ipr_id) for ipr_id in sorted(iprs)))

    return HttpResponse("\n".join(lines), content_type="text/plain")

def new(request, type, updates=None):
    """Submit a new IPR Disclosure.  If the updates field != None, this disclosure
    updates one or more other disclosures."""
    
    DraftFormset = inlineformset_factory(IprDisclosureBase, IprDocRel, form=DraftForm, can_delete=False, extra=1)
    RfcFormset = inlineformset_factory(IprDisclosureBase, IprDocRel, form=RfcForm, can_delete=False, extra=1)

    if request.method == 'POST':
        form = ipr_form_mapping[type](request.POST)
        if not type == 'generic':
            draft_formset = DraftFormset(request.POST, instance=IprDisclosureBase(), prefix='draft')
            rfc_formset = RfcFormset(request.POST, instance=IprDisclosureBase(), prefix='rfc')
        else:
            draft_formset = None
            rfc_formset = None
            
        if request.user.is_anonymous():
            person = Person.objects.get(name="(System)")
        else:
            person = request.user.person
            
        # check formset validity
        if not type == 'generic':
            valid_formsets = draft_formset.is_valid() and rfc_formset.is_valid()
        else:
            valid_formsets = True
            
        if form.is_valid() and valid_formsets:
            updates = form.cleaned_data.get('updates')
            disclosure = form.save(commit=False)
            disclosure.by = person
            disclosure.state = IprDisclosureStateName.objects.get(slug='pending')
            disclosure.save()
            
            if not type == 'generic':
                draft_formset = DraftFormset(request.POST, instance=disclosure, prefix='draft')
                draft_formset.save()
                rfc_formset = RfcFormset(request.POST, instance=disclosure, prefix='rfc')
                rfc_formset.save()

            set_disclosure_title(disclosure)
            disclosure.save()
            
            if updates:
                for ipr in updates:
                    RelatedIpr.objects.create(source=disclosure,target=ipr,relationship_id='updates')
                
            # create IprEvent
            IprEvent.objects.create(
                type_id='submitted',
                by=person,
                disclosure=disclosure,
                desc="Disclosure Submitted")

            # send email notification
            send_mail(request, settings.IPR_EMAIL_TO, ('IPR Submitter App', 'ietf-ipr@ietf.org'),
                'New IPR Submission Notification',
                "ipr/new_update_email.txt",
                {"ipr": disclosure,})
            
            return render("ipr/submitted.html", context_instance=RequestContext(request))

    else:
        if updates:
            form = ipr_form_mapping[type](initial={'updates':str(updates)})
        else:
            form = ipr_form_mapping[type]()
        disclosure = IprDisclosureBase()    # dummy disclosure for inlineformset
        draft_formset = DraftFormset(instance=disclosure, prefix='draft')
        rfc_formset = RfcFormset(instance=disclosure, prefix='rfc')
        
    return render("ipr/details_edit.html",  {
        'form': form,
        'draft_formset':draft_formset,
        'rfc_formset':rfc_formset,
        'type':type},
        context_instance=RequestContext(request)
    )

@role_required('Secretariat',)
def notify(request, id, type):
    """Send email notifications.
    type = update: send notice to old ipr submitter(s)
    type = posted: send notice to submitter, etc. that new IPR was posted
    """
    ipr = get_object_or_404(IprDisclosureBase, id=id).get_child()
    NotifyFormset = formset_factory(NotifyForm,extra=0)
    
    if request.method == 'POST':
        formset = NotifyFormset(request.POST)
        if formset.is_valid():
            for form in formset.forms:
                message = infer_message(form.cleaned_data['text'])
                message.by = request.user.person
                message.save()
                send_mail_message(None,message)
                IprEvent.objects.create(
                    type_id = form.cleaned_data['type'],
                    by = request.user.person,
                    disclosure = ipr,
                    response_due = datetime.datetime.now().date() + datetime.timedelta(days=30),
                    message = message,
                )
            messages.success(request,'Notifications send')
            return redirect("ipr_show", id=ipr.id)
            
    else:
        if type == 'update':
            initial = [ {'type':'update_notify','text':m} for m in get_update_submitter_emails(ipr) ]
        else:
            initial = [ {'type':'msgout','text':m} for m in get_posted_emails(ipr) ]
        formset = NotifyFormset(initial=initial)
        
    return render("ipr/notify.html", {
        'formset': formset,
        'ipr': ipr},
        context_instance=RequestContext(request)
    )

@role_required('Secretariat',)
def post(request, id):
    """Post the disclosure and redirect to notification view"""
    ipr = get_object_or_404(IprDisclosureBase, id=id).get_child()
    person = request.user.person
    
    ipr.state = IprDisclosureStateName.objects.get(slug='posted')
    ipr.save()
    
    # create event
    IprEvent.objects.create(
        type_id='posted',
        by=person,
        disclosure=ipr,
        desc="Disclosure Posted")
    
    messages.success(request, 'Disclosure Posted')
    return redirect("ipr_notify", id=ipr.id, type='posted')
    
def search(request):
    search_type = request.GET.get("submit")
    if search_type:
        form = SearchForm(request.GET)
        docid = request.GET.get("id") or request.GET.get("id_document_tag") or ""
        docs = doc = None
        iprs = []
        
        # set states
        states = request.GET.getlist('state',('posted',))
        if states == ['all']:
            states = IprDisclosureStateName.objects.values_list('slug',flat=True)
        
        # get query field
        q = ''
        if request.GET.get(search_type):
            q = request.GET.get(search_type)

        if q or docid:
            # Search by RFC number or draft-identifier
            # Document list with IPRs
            if search_type in ["draft", "rfc"]:
                doc = q

                if docid:
                    start = DocAlias.objects.filter(name=docid)
                else:
                    if search_type == "draft":
                        q = normalize_draftname(q)
                        start = DocAlias.objects.filter(name__contains=q, name__startswith="draft")
                    elif search_type == "rfc":
                        start = DocAlias.objects.filter(name="rfc%s" % q.lstrip("0"))
                
                # one match
                if len(start) == 1:
                    first = start[0]
                    doc = str(first)
                    docs = related_docs(first)
                    iprs, docs = iprs_from_docs(docs,states)
                    template = "ipr/search_doc_result.html"
                # multiple matches, select just one
                elif start:
                    docs = start
                    template = "ipr/search_doc_list.html"
                # no match
                else:
                    template = "ipr/search_doc_result.html"

            # Search by legal name
            # IPR list with documents
            elif search_type == "holder":
                #assert False, (q,search_type,states)
                iprs = IprDisclosureBase.objects.filter(holder_legal_name__icontains=q, state_id__in=states)
                template = "ipr/search_holder_result.html"
                
            # Search by patents field or content of emails for patent numbers
            # IPR list with documents
            elif search_type == "patent":
                iprs = IprDisclosureBase.objects.filter(state_id__in=states)
                iprs = iprs.filter(Q(holderiprdisclosure__patent_info__icontains=q) |
                                   Q(thirdpartyiprdisclosure__patent_info__icontains=q) |
                                   Q(nondocspecificiprdisclosure__patent_info__icontains=q))
                template = "ipr/search_patent_result.html"

            # Search by wg acronym
            # Document list with IPRs
            elif search_type == "group":
                docs = list(DocAlias.objects.filter(document__group=q))
                related = []
                for doc in docs:
                    doc.product_of_this_wg = True
                    related += related_docs(doc)
                iprs, docs = iprs_from_docs(list(set(docs+related)),states)
                docs = [ doc for doc in docs if doc.iprs ]
                docs = sorted(docs, key=lambda x: max([ipr.submitted_date for ipr in x.iprs]), reverse=True)
                template = "ipr/search_wg_result.html"
                
            # Search by rfc and id title
            # Document list with IPRs
            elif search_type == "doctitle":
                docs = list(DocAlias.objects.filter(document__title__icontains=q))
                related = []
                for doc in docs:
                    related += related_docs(doc)
                iprs, docs = iprs_from_docs(list(set(docs+related)),states)
                docs = [ doc for doc in docs if doc.iprs ]
                docs = sorted(docs, key=lambda x: max([ipr.submitted_date for ipr in x.iprs]), reverse=True)
                template = "ipr/search_doctitle_result.html"

            # Search by title of IPR disclosure
            # IPR list with documents
            elif search_type == "iprtitle":
                iprs = IprDisclosureBase.objects.filter(title__icontains=q, state_id__in=states)
                template = "ipr/search_iprtitle_result.html"

            else:
                raise Http404("Unexpected search type in IPR query: %s" % search_type)
                
            # sort and render response
            iprs = [ ipr for ipr in iprs if not ipr.updated_by.all() ]
            if has_role(request.user, "Secretariat"):
                iprs = sorted(iprs, key=lambda x: (x.submitted_date,x.id), reverse=True)
                iprs = sorted(iprs, key=lambda x: x.state.order)
            else:
                iprs = sorted(iprs, key=lambda x: (x.submitted_date,x.id), reverse=True)
            
            return render(template, {
                "q": q,
                "iprs": iprs,
                "docs": docs,
                "doc": doc,
                "form":form},
                context_instance=RequestContext(request)
            )

        return HttpResponseRedirect(request.path)

    else:
        form = SearchForm(initial={'state':['all']})
        return render("ipr/search.html", {"form":form }, context_instance=RequestContext(request))

def show(request, id):
    """View of individual declaration"""
    ipr = get_object_or_404(IprDisclosureBase, id=id).get_child()
    if not has_role(request.user, 'Secretariat'):
        if ipr.state.slug == 'removed':
            return render("ipr/removed.html",  {
                'ipr': ipr},
                context_instance=RequestContext(request)
            )
        elif ipr.state.slug != 'posted':
            raise Http404

    tabs = [('Disclosure','disclosure',urlreverse('ipr_show',kwargs={'id':id}),True),
            ('History','history',urlreverse('ipr_history',kwargs={'id':id}),True)]

    return render("ipr/details_view.html",  {
        'ipr': ipr,
        'tabs':tabs,
        'selected':'disclosure'},
        context_instance=RequestContext(request)
    )

def showlist(request):
    """List all disclosures by type, posted only"""
    generic = GenericIprDisclosure.objects.filter(state='posted').prefetch_related('relatedipr_source_set__target','relatedipr_target_set__source').order_by('-time')
    specific = HolderIprDisclosure.objects.filter(state='posted').prefetch_related('relatedipr_source_set__target','relatedipr_target_set__source').order_by('-time')
    thirdpty = ThirdPartyIprDisclosure.objects.filter(state='posted').prefetch_related('relatedipr_source_set__target','relatedipr_target_set__source').order_by('-time')
    nondocspecific = NonDocSpecificIprDisclosure.objects.filter(state='posted').prefetch_related('relatedipr_source_set__target','relatedipr_target_set__source').order_by('-time')
    
    # combine nondocspecific with generic and re-sort
    generic = itertools.chain(generic,nondocspecific)
    generic = sorted(generic, key=lambda x: x.time,reverse=True)
    
    return render("ipr/list.html", {
            'generic_disclosures' : generic,
            'specific_disclosures': specific,
            'thirdpty_disclosures': thirdpty}, 
            context_instance=RequestContext(request)
    )

@role_required('Secretariat',)
def state(request, id):
    """Change the state of the disclosure"""
    ipr = get_object_or_404(IprDisclosureBase, id=id)
    login = request.user.person

    if request.method == 'POST':
        form = StateForm(request.POST)
        if form.is_valid():
            ipr.state = form.cleaned_data.get('state')
            ipr.save()
            IprEvent.objects.create(
                by=login,
                type_id=ipr.state.pk,
                disclosure=ipr,
                desc="State Changed to %s" % ipr.state.name
            )
            if form.cleaned_data.get('comment'):
                if form.cleaned_data.get('private'):
                    type_id = 'private_comment'
                else:
                    type_id = 'comment'
                
                IprEvent.objects.create(
                    by=login,
                    type_id=type_id,
                    disclosure=ipr,
                    desc=form.cleaned_data['comment']
                )
            messages.success(request, 'State Changed')
            return redirect("ipr_show", id=ipr.id)
    else:
        form = StateForm(initial={'state':ipr.state.pk,'private':True})
  
    return render('ipr/state.html',dict(ipr=ipr,form=form),
        context_instance=RequestContext(request))

# use for link to update specific IPR
def update(request, id):
    """Calls the 'new' view with updates parameter"""
    # determine disclosure type
    ipr = get_object_or_404(IprDisclosureBase,id=id)
    child = ipr.get_child()
    type = class_to_type[child.get_classname()]
    return new(request, type, updates=id)