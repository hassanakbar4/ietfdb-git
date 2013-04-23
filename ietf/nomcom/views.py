 # -*- coding: utf-8 -*-
import datetime

from django.views.generic.create_update import delete_object
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.http import HttpResponse, Http404, HttpResponseRedirect, HttpResponseForbidden
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.template.loader import render_to_string
from django.utils import simplejson
from django.db.models import Count, Q
from django.forms.models import modelformset_factory, inlineformset_factory

from ietf.utils.mail import send_mail

from ietf.dbtemplate.models import DBTemplate
from ietf.dbtemplate.views import template_edit
from ietf.name.models import NomineePositionState, FeedbackType

from ietf.nomcom.decorators import member_required, private_key_required
from ietf.nomcom.forms import (NominateForm, FeedbackForm, QuestionnaireForm,
                               MergeForm, NomComTemplateForm, PositionForm,
                               PrivateKeyForm, EditNomcomForm, PendingFeedbackForm)
from ietf.nomcom.models import Position, NomineePosition, Nominee, Feedback, NomCom, ReminderDates
from ietf.nomcom.utils import (get_nomcom_by_year, HOME_TEMPLATE,
                               store_nomcom_private_key, get_hash_nominee_position,
                               NOMINEE_REMINDER_TEMPLATE)


def index(request, year):
    nomcom = get_nomcom_by_year(year)
    home_template = '/nomcom/%s/%s' % (nomcom.group.acronym, HOME_TEMPLATE)
    template = render_to_string(home_template, {})
    return render_to_response('nomcom/index.html',
                              {'nomcom': nomcom,
                               'year': year,
                               'selected': 'index',
                               'template': template}, RequestContext(request))


@member_required(role='member')
def private_key(request, year):
    nomcom = get_nomcom_by_year(year)

    back_url = request.GET.get('back_to', reverse('nomcom_private_index', None, args=(year, )))
    if request.method == 'POST':
        form = PrivateKeyForm(data=request.POST)
        if form.is_valid():
            store_nomcom_private_key(request, year, form.cleaned_data.get('key', ''))
            return HttpResponseRedirect(back_url)
    else:
        form = PrivateKeyForm()
    return render_to_response('nomcom/private_key.html',
                              {'nomcom': nomcom,
                               'year': year,
                               'back_url': back_url,
                               'form': form,
                               'selected': 'private_key'}, RequestContext(request))


@member_required(role='member')
def private_index(request, year):
    nomcom = get_nomcom_by_year(year)
    all_nominee_positions = NomineePosition.objects.get_by_nomcom(nomcom).not_duplicated()
    is_chair = nomcom.group.is_chair(request.user)
    message = None
    if is_chair and request.method == 'POST':
        action = request.POST.get('action')
        nominations_to_modify = request.POST.getlist('selected')
        if nominations_to_modify:
            nominations = all_nominee_positions.filter(id__in=nominations_to_modify)
            if action == "set_as_accepted":
                nominations.update(state='accepted')
                message = ('success', 'The selected nominations have been set as accepted')
            elif action == "set_as_declined":
                nominations.update(state='declined')
                message = ('success', 'The selected nominations have been set as declined')
            elif action == "set_as_pending":
                nominations.update(state='pending')
                message = ('success', 'The selected nominations have been set as pending')
        else:
            message = ('warning', "Please, select some nominations to work with")

    filters = {}
    questionnaire_state = "questionnaire"
    selected_state = request.GET.get('state')
    selected_position = request.GET.get('position')

    if selected_state and not selected_state == questionnaire_state:
        filters['state__slug'] = selected_state

    if selected_position:
        filters['position__id'] = selected_position

    nominee_positions = all_nominee_positions
    if filters:
        nominee_positions = nominee_positions.filter(**filters)

    if selected_state == questionnaire_state:
        nominee_positions = [np for np in nominee_positions if np.questionnaires]

    stats = all_nominee_positions.values('position__name', 'position__id').annotate(total=Count('position'))
    states = list(NomineePositionState.objects.values('slug', 'name')) + [{'slug': questionnaire_state, 'name': u'Questionnaire'}]
    positions = all_nominee_positions.values('position__name', 'position__id').distinct()
    for s in stats:
        for state in states:
            if state['slug'] == questionnaire_state:
                s[state['slug']] = Feedback.objects.filter(positions__id=s['position__id'], type='questio').count()
            else:
                s[state['slug']] = all_nominee_positions.filter(position__name=s['position__name'],
                                                                state=state['slug']).count()

    return render_to_response('nomcom/private_index.html',
                              {'nomcom': nomcom,
                               'year': year,
                               'nominee_positions': nominee_positions,
                               'stats': stats,
                               'states': states,
                               'positions': positions,
                               'selected_state': selected_state,
                               'selected_position': selected_position and int(selected_position) or None,
                               'selected': 'index',
                               'is_chair': is_chair,
                               'message': message}, RequestContext(request))


@member_required(role='chair')
def send_reminder_mail(request, year):
    nomcom = get_nomcom_by_year(year)
    nominees = Nominee.objects.get_by_nomcom(nomcom).not_duplicated().filter(nomineeposition__state='pending').distinct()
    nomcom_template_path = '/nomcom/%s/' % nomcom.group.acronym
    mail_path = nomcom_template_path + NOMINEE_REMINDER_TEMPLATE
    mail_template = DBTemplate.objects.filter(group=nomcom.group, path=mail_path)
    mail_template = mail_template and mail_template[0] or None
    message = None

    if request.method == 'POST':
        selected_nominees = request.POST.getlist('selected')
        selected_nominees = nominees.filter(id__in=selected_nominees)
        if selected_nominees:
            subject = 'IETF Nomination Information'
            from_email = settings.NOMCOM_FROM_EMAIL
            for nominee in nominees:
                to_email = nominee.email.address
                positions = ', '.join([nominee_position.position.name for nominee_position in nominee.nomineeposition_set.pending()])
                context = {'positions': positions}
                send_mail(None, to_email, from_email, subject, mail_path, context)
            message = ('success', 'An query has been sent to each person, asking them to accept (or decline) the nominations')
        else:
            message = ('warning', "Please, select some nominee")
    return render_to_response('nomcom/send_reminder_mail.html',
                              {'nomcom': nomcom,
                               'year': year,
                               'nominees': nominees,
                               'mail_template': mail_template,
                               'message': message}, RequestContext(request))


@member_required(role='chair')
def private_merge(request, year):
    nomcom = get_nomcom_by_year(year)
    message = None
    if request.method == 'POST':
        form = MergeForm(request.POST, nomcom=nomcom)
        if form.is_valid():
            form.save()
            message = ('success', 'The emails have been unified')
    else:
        form = MergeForm(nomcom=nomcom)

    return render_to_response('nomcom/private_merge.html',
                              {'nomcom': nomcom,
                               'year': year,
                               'form': form,
                               'message': message,
                               'selected': 'merge'}, RequestContext(request))


def requirements(request, year):
    nomcom = get_nomcom_by_year(year)
    positions = nomcom.position_set.all()
    return render_to_response('nomcom/requirements.html',
                              {'nomcom': nomcom,
                               'positions': positions,
                               'year': year,
                               'selected': 'requirements'}, RequestContext(request))


def questionnaires(request, year):
    nomcom = get_nomcom_by_year(year)
    positions = nomcom.position_set.all()
    return render_to_response('nomcom/questionnaires.html',
                              {'nomcom': nomcom,
                               'positions': positions,
                               'year': year,
                               'selected': 'questionnaires'}, RequestContext(request))


@login_required
def public_nominate(request, year):
    return nominate(request, year, True)


@member_required(role='member')
def private_nominate(request, year):
    return nominate(request, year, False)


def nominate(request, year, public):
    nomcom = get_nomcom_by_year(year)
    has_publickey = nomcom.public_key and True or False
    if public:
        template = 'nomcom/public_nominate.html'
    else:
        template = 'nomcom/private_nominate.html'

    if not has_publickey:
            message = ('warning', "Nomcom don't have public key to ecrypt data, please contact with nomcom chair")
            return render_to_response(template,
                              {'has_publickey': has_publickey,
                               'message': message,
                               'nomcom': nomcom,
                               'year': year,
                               'selected': 'nominate'}, RequestContext(request))

    message = None
    if request.method == 'POST':
        form = NominateForm(data=request.POST, nomcom=nomcom, user=request.user, public=public)
        if form.is_valid():
            form.save()
            message = ('success', 'Your nomination has been registered. Thank you for the nomination.')
    else:
        form = NominateForm(nomcom=nomcom, user=request.user, public=public)

    return render_to_response(template,
                              {'has_publickey': has_publickey,
                               'form': form,
                               'message': message,
                               'nomcom': nomcom,
                               'year': year,
                               'selected': 'nominate'}, RequestContext(request))


@login_required
def public_feedback(request, year):
    return feedback(request, year, True)


@member_required(role='member')
def private_feedback(request, year):
    return feedback(request, year, False)


def feedback(request, year, public):
    nomcom = get_nomcom_by_year(year)
    has_publickey = nomcom.public_key and True or False
    submit_disabled = True
    nominee = None
    position = None
    selected_nominee = request.GET.get('nominee')
    selected_position = request.GET.get('position')
    if selected_nominee and selected_position:
        nominee = get_object_or_404(Nominee, id=selected_nominee)
        position = get_object_or_404(Position, id=selected_position)
        submit_disabled = False

    positions = Position.objects.get_by_nomcom(nomcom=nomcom).opened()

    if public:
        template = 'nomcom/public_feedback.html'
    else:
        template = 'nomcom/private_feedback.html'

    if not has_publickey:
            message = ('warning', "Nomcom don't have public key to ecrypt data, please contact with nomcom chair")
            return render_to_response(template,
                              {'has_publickey': has_publickey,
                               'message': message,
                               'nomcom': nomcom,
                               'year': year,
                               'selected': 'feedback'}, RequestContext(request))

    message = None
    if request.method == 'POST':
        form = FeedbackForm(data=request.POST,
                            nomcom=nomcom, user=request.user,
                            public=public, position=position, nominee=nominee)
        if form.is_valid():
            form.save()
            message = ('success', 'Your feedback has been registered.')
    else:
        form = FeedbackForm(nomcom=nomcom, user=request.user, public=public,
                            position=position, nominee=nominee)

    return render_to_response(template,
                              {'has_publickey': has_publickey,
                               'form': form,
                               'message': message,
                               'nomcom': nomcom,
                               'year': year,
                               'positions': positions,
                               'submit_disabled': submit_disabled,
                               'selected': 'feedback'}, RequestContext(request))


@member_required(role='chair')
def private_questionnaire(request, year):
    nomcom = get_nomcom_by_year(year)
    has_publickey = nomcom.public_key and True or False
    message = None
    template = 'nomcom/private_questionnaire.html'

    if not has_publickey:
            message = ('warning', "Nomcom don't have public key to ecrypt data, please contact with nomcom chair")
            return render_to_response(template,
                              {'has_publickey': has_publickey,
                               'message': message,
                               'nomcom': nomcom,
                               'year': year,
                               'selected': 'questionnaire'}, RequestContext(request))

    if request.method == 'POST':
        form = QuestionnaireForm(data=request.POST,
                                 nomcom=nomcom, user=request.user)
        if form.is_valid():
            form.save()
            message = ('success', 'The questionnaire has been registered.')
    else:
        form = QuestionnaireForm(nomcom=nomcom, user=request.user)

    return render_to_response(template,
                              {'has_publickey': has_publickey,
                               'form': form,
                               'message': message,
                               'nomcom': nomcom,
                               'year': year,
                               'selected': 'questionnaire'}, RequestContext(request))


def process_nomination_status(request, year, nominee_position_id, state, date, hash):
    valid = get_hash_nominee_position(date, nominee_position_id) == hash
    if not valid:
        return HttpResponseForbidden("Bad hash!")
    expiration_days = getattr(settings, 'DAYS_TO_EXPIRE_NOMINATION_LINK', None)
    if expiration_days:
        request_date = datetime.date(int(date[:4]), int(date[4:6]), int(date[6:]))
        if datetime.date.today() > (request_date + datetime.timedelta(days=settings.DAYS_TO_EXPIRE_REGISTRATION_LINK)):
            return HttpResponseForbidden("Link expired")

    need_confirmation = True
    nomcom = get_nomcom_by_year(year)
    nominee_position = get_object_or_404(NomineePosition, id=nominee_position_id)
    if nominee_position.state.slug != "pending":
        return HttpResponseForbidden("The nomination already was %s" % nominee_position.state)

    state = get_object_or_404(NomineePositionState, slug=state)
    message = ('warning', "Are you sure to change the nomination on %s as %s?" % (nominee_position.position.name,
                                                                                  state.name))
    if request.method == 'POST':
        nominee_position.state = state
        nominee_position.save()
        need_confirmation = False
        message = message = ('success', 'Your nomination on %s has been set as %s' % (nominee_position.position.name,
                                                                                      state.name))

    return render_to_response('nomcom/process_nomination_status.html',
                              {'message': message,
                               'nomcom': nomcom,
                               'year': year,
                               'nominee_position': nominee_position,
                               'state': state,
                               'need_confirmation': need_confirmation,
                               'selected': 'feedback'}, RequestContext(request))


@member_required(role='member')
@private_key_required
def view_feedback(request, year):
    nomcom = get_nomcom_by_year(year)
    nominees = Nominee.objects.get_by_nomcom(nomcom).not_duplicated().distinct()

    return render_to_response('nomcom/view_feedback.html',
                              {'year': year,
                               'selected': 'view_feedback',
                               'nominees': nominees,
                               'nomcom': nomcom}, RequestContext(request))


@member_required(role='chair')
@private_key_required
def view_feedback_pending(request, year):
    nomcom = get_nomcom_by_year(year)
    message = None
    FeedbackFormSet = modelformset_factory(Feedback,
                                           form=PendingFeedbackForm,
                                           exclude=('nomcom', 'comments'),
                                           extra=0)
    feedbacks = Feedback.objects.filter(Q(type__isnull=True) |
                                        Q(nominees__isnull=True) |
                                        Q(positions__isnull=True))
    if request.method == 'POST':
        formset = FeedbackFormSet(request.POST)
        for form in formset.forms:
            form.set_nomcom(nomcom, request.user)
        if formset.is_valid():
            formset.save()
            message = ('success', 'The feedbacks has been saved.')
            formset = FeedbackFormSet(queryset=feedbacks)
            for form in formset.forms:
                form.set_nomcom(nomcom, request.user)
    else:
        formset = FeedbackFormSet(queryset=feedbacks)
        for form in formset.forms:
            form.set_nomcom(nomcom, request.user)
    return render_to_response('nomcom/view_feedback_pending.html',
                              {'year': year,
                               'selected': 'view_feedback',
                               'formset': formset,
                               'message': message,
                               'nomcom': nomcom}, RequestContext(request))


@member_required(role='member')
@private_key_required
def view_feedback_nominee(request, year, nominee_id):
    nomcom = get_nomcom_by_year(year)
    nominee = get_object_or_404(Nominee, id=nominee_id)
    feedback_types = FeedbackType.objects.all()

    return render_to_response('nomcom/view_feedback_nominee.html',
                              {'year': year,
                               'selected': 'view_feedback',
                               'nominee': nominee,
                               'feedback_types': feedback_types,
                               'nomcom': nomcom}, RequestContext(request))


@member_required(role='chair')
def edit_nomcom(request, year):
    nomcom = get_nomcom_by_year(year)

    message = ('warning', 'Previous data will remain encrypted with the old key')

    ReminderDateInlineFormSet = inlineformset_factory(NomCom, ReminderDates)
    if request.method == 'POST':
        formset = ReminderDateInlineFormSet(request.POST, instance=nomcom)
        form = EditNomcomForm(request.POST,
                              request.FILES,
                              instance=nomcom)
        if form.is_valid() and formset.is_valid():
            form.save()
            formset.save()
            formset = ReminderDateInlineFormSet(instance=nomcom)
            message = ('success', 'The nomcom has been changed')
    else:
        formset = ReminderDateInlineFormSet(instance=nomcom)
        form = EditNomcomForm(instance=nomcom)

    return render_to_response('nomcom/edit_nomcom.html',
                              {'form': form,
                               'formset': formset,
                               'nomcom': nomcom,
                               'message': message,
                               'year': year,
                               'selected': 'edit_nomcom'}, RequestContext(request))


@member_required(role='chair')
def delete_nomcom(request, year):
    nomcom = get_nomcom_by_year(year)
    post_delete_redirect = reverse('nomcom_deleted')
    extra_context = {'year': year,
                     'selected': 'edit_nomcom',
                     'nomcom': nomcom}

    return delete_object(request,
                         model=NomCom,
                         object_id=nomcom.id,
                         post_delete_redirect=post_delete_redirect,
                         template_name='nomcom/delete_nomcom.html',
                         extra_context=extra_context)


@member_required(role='chair')
def list_templates(request, year):
    nomcom = get_nomcom_by_year(year)
    positions = nomcom.position_set.all()
    template_list = DBTemplate.objects.filter(group=nomcom.group).exclude(path__contains='/position/')

    return render_to_response('nomcom/list_templates.html',
                              {'template_list': template_list,
                               'positions': positions,
                               'year': year,
                               'selected': 'edit_templates',
                               'nomcom': nomcom}, RequestContext(request))


@member_required(role='chair')
def edit_template(request, year, template_id):
    nomcom = get_nomcom_by_year(year)
    return_url = request.META.get('HTTP_REFERER', None)

    return template_edit(request, nomcom.group.acronym, template_id,
                         base_template='nomcom/edit_template.html',
                         formclass=NomComTemplateForm,
                         extra_context={'year': year,
                                        'return_url': return_url,
                                        'nomcom': nomcom})


@member_required(role='chair')
def list_positions(request, year):
    nomcom = get_nomcom_by_year(year)
    positions = nomcom.position_set.all()

    return render_to_response('nomcom/list_positions.html',
                              {'positions': positions,
                               'year': year,
                               'selected': 'edit_positions',
                               'nomcom': nomcom}, RequestContext(request))


@member_required(role='chair')
def remove_position(request, year, position_id):
    nomcom = get_nomcom_by_year(year)
    try:
        position = nomcom.position_set.get(id=position_id)
    except Position.DoesNotExist:
        raise Http404

    if request.POST.get('remove', None):
        position.delete()
        return HttpResponseRedirect(reverse('nomcom_list_positions', None, args=(year, )))
    return render_to_response('nomcom/remove_position.html',
                              {'year': year,
                               'position': position,
                               'nomcom': nomcom}, RequestContext(request))


@member_required(role='chair')
def edit_position(request, year, position_id=None):
    nomcom = get_nomcom_by_year(year)
    if position_id:
        try:
            position = nomcom.position_set.get(id=position_id)
        except Position.DoesNotExist:
            raise Http404
    else:
        position = None

    if request.method == 'POST':
        form = PositionForm(request.POST, instance=position, nomcom=nomcom)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse('nomcom_list_positions', None, args=(year, )))
    else:
        form = PositionForm(instance=position, nomcom=nomcom)

    return render_to_response('nomcom/edit_position.html',
                              {'form': form,
                               'position': position,
                               'year': year,
                               'nomcom': nomcom}, RequestContext(request))


def ajax_position_text(request, position_id):
    try:
        position_text = Position.objects.get(id=position_id).initial_text
    except Position.DoesNotExist:
        position_text = ""

    result = {'text': position_text}

    json_result = simplejson.dumps(result)
    return HttpResponse(json_result, mimetype='application/json')
