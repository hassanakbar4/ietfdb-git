# Copyright The IETF Trust 2007, All Rights Reserved

from django.conf.urls.defaults import patterns
from ietf.idsubmit import views
from ietf.idsubmit.models import IdSubmissionDetail, TempIdAuthors

queryset_idsubmit = IdSubmissionDetail.objects.all()

urlpatterns = patterns('',
     (r'^$', views.file_upload),
     (r'^upload/$', views.file_upload),
     (r'^auto_post/', views.trigger_auto_post),
     (r'^adjust/(?P<submission_id_or_name>\d+)/$', views.adjust_form),
     (r'^cancel/(?P<submission_id>\d+)/$', views.cancel_draft),
     (r'^status/(?P<submission_id_or_name>.+)/$', views.draft_status),
     (r'^status/(?P<submission_id_or_name>.+)$', views.draft_status),
     (r'^status/$', views.draft_status),
     (r'^status/?passed_filename=(?P<filename>.+)/$', views.draft_status),
     (r'^manual_post/$', views.manual_post),
     (r'^verify/(?P<submission_id>\d+)/(?P<auth_key>\w+)/$', views.verify_key),
     (r'^verify/(?P<submission_id>\d+)/(?P<auth_key>\w+)/(?P<from_wg_or_sec>(wg|sec))/$', views.verify_key),
)
urlpatterns += patterns('django.views.generic.list_detail',
        (r'^viewfirsttwo/(?P<object_id>\d+)/$', 'object_detail', { 'queryset': queryset_idsubmit, 'template_name':"idsubmit/first_two_pages.html" }),
        (r'^displayidnits/(?P<object_id>\d+)/$', 'object_detail', { 'queryset': queryset_idsubmit, 'template_name':"idsubmit/idnits.html" }),
)
