from ietf.idtracker.models import IETFWG, InternetDraft, IESGLogin
from django.shortcuts import get_object_or_404, render_to_response
from django.template import RequestContext
from django.http import HttpResponseForbidden

from ietf.idrfc.views_search import SearchForm, search_query
from ietf.wgchairs.forms import (RemoveDelegateForm, add_form_factory,
                                 ManagingShepherdForm, workflow_form_factory,
                                 TransitionFormSet)
from ietf.wgchairs.accounts import (can_manage_delegates_in_group, get_person_for_user,
                                    can_manage_shepherds_in_group,
                                    can_manage_workflow_in_group)
from ietf.ietfworkflows.utils import (get_workflow_for_wg,
                                      get_default_workflow_for_wg)


def manage_delegates(request, acronym):
    wg = get_object_or_404(IETFWG, group_acronym__acronym=acronym, group_type=1)
    user = request.user
    if not can_manage_delegates_in_group(user, wg):
        return HttpResponseForbidden('You have no permission to access this view')
    delegates = wg.wgdelegate_set.all()
    add_form = add_form_factory(request, wg, user)
    if request.method == 'POST':
        if request.POST.get('remove', None):
            form = RemoveDelegateForm(wg=wg, data=request.POST.copy())
            if form.is_valid():
                form.save()
        elif add_form.is_valid():
            add_form.save()
            add_form = add_form.get_next_form()
    return render_to_response('wgchairs/manage_delegates.html',
                              {'wg': wg,
                               'delegates': delegates,
                               'selected': 'manage_delegates',
                               'can_add': delegates.count() < 3,
                               'add_form': add_form,
                              }, RequestContext(request))


def manage_workflow(request, acronym):
    wg = get_object_or_404(IETFWG, group_acronym__acronym=acronym, group_type=1)
    user = request.user
    if not can_manage_workflow_in_group(user, wg):
        return HttpResponseForbidden('You have no permission to access this view')
    workflow = get_workflow_for_wg(wg)
    default_workflow = get_default_workflow_for_wg()
    formset = None
    if request.method == 'POST':
        form = workflow_form_factory(request, wg=wg, user=user)
        if form.is_valid():
            form.save()
        elif isinstance(form, TransitionFormSet):
            formset = form
    tags = workflow.selected_tags.all()
    default_tags = default_workflow.annotation_tags.all()
    states = workflow.selected_states.all()
    default_states = default_workflow.states.all()
    for i in default_states:
        if states.filter(name=i.name).count() == 1:
            i.used = True
    for i in default_tags:
        if tags.filter(name=i.name).count() == 1:
            i.used = True
    if not formset:
        formset = TransitionFormSet(queryset=workflow.transitions.all(), user=user, wg=wg)

    return render_to_response('wgchairs/manage_workflow.html',
                              {'wg': wg,
                               'workflow': workflow,
                               'default_workflow': default_workflow,
                               'states': states,
                               'tags': tags,
                               'default_states': default_states,
                               'default_tags': default_tags,
                               'formset': formset,
                              }, RequestContext(request))


def managing_shepherd(request, acronym, name):
    """
     View for managing the assigned shepherd of a document.
    """
    doc = get_object_or_404(InternetDraft, filename=name)
    login = IESGLogin.objects.get(login_name=request.user.username)
    form = ManagingShepherdForm()
    if request.method == "POST":
        form = ManagingShepherdForm(request.POST, current_person=login.person)
        if form.is_valid():
            form.change_shepherd(doc)

    return render_to_response('wgchairs/edit_management_shepherd.html',
                              dict(doc=doc,
                                   form=form,
                                   user=request.user,
                                   login=login),
                              context_instance=RequestContext(request))


def wg_shepherd_documents(request, acronym):
    wg = get_object_or_404(IETFWG, group_acronym__acronym=acronym, group_type=1)
    user = request.user
    if not can_manage_shepherds_in_group(user, wg):
        return HttpResponseForbidden('You have no permission to access this view')
    current_person = get_person_for_user(user)

    form = SearchForm({'by': 'group', 'group': str(wg.group_acronym.acronym),
                       'activeDrafts': 'on'})
    if not form.is_valid():
        raise ValueError("form did not validate")
    (docs, meta) = search_query(form.cleaned_data)

    base_qs = InternetDraft.objects.filter(pk__in=[i.id._draft.pk for i in docs if i.id]).select_related('status')
    documents_no_shepherd = base_qs.filter(shepherd__isnull=True)
    documents_my = base_qs.filter(shepherd=current_person)
    documents_other = base_qs.exclude(shepherd__isnull=True).exclude(shepherd__pk__in=[current_person.pk, 0])
    context = {
        'no_shepherd': documents_no_shepherd,
        'my_documents': documents_my,
        'other_shepherds': documents_other,
        'wg': wg,
    }
    return render_to_response('wgchairs/wg_shepherd_documents.html', context, RequestContext(request))
