# Copyright The IETF Trust 2007, All Rights Reserved

from django.conf.urls import patterns, include
from django.conf import settings

urlpatterns = patterns('',
    (r'^$', 'ietf.group.views.active_groups'), 
    (r'^groupmenu.json', 'ietf.group.views_ajax.group_menu_data', None, "group_menu_data"),
    (r'^%(acronym)s.json$' % settings.URL_REGEXPS, 'ietf.group.views_ajax.group_json'),
    (r'^chartering/$', 'ietf.group.views.chartering_groups'),
    (r'^chartering/create/(?P<group_type>(wg|rg))/$', 'ietf.group.views_edit.edit', {'action': "charter"}, "group_create"),
    (r'^concluded/$', 'ietf.group.views.concluded_groups'),
    (r'^email-aliases/$', 'ietf.group.views.email_aliases'),
    (r'^all-status/$', 'ietf.group.views.all_status'),

    (r'^%(acronym)s/$' % settings.URL_REGEXPS, 'ietf.group.views.group_home', None, "group_home"),
    (r'^%(acronym)s/' % settings.URL_REGEXPS, include('ietf.group.urls_info_details')),
)

