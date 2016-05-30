# Autogenerated by the mkresources management command 2014-11-13 23:53
from tastypie.resources import ModelResource
from tastypie.fields import ToOneField
from tastypie.constants import ALL, ALL_WITH_RELATIONS
from tastypie.cache import SimpleCache

from ietf import api

from ietf.submit.models import Preapproval, \
    SubmissionCheck, Submission, SubmissionEmail, SubmissionEvent


from ietf.person.resources import PersonResource
class PreapprovalResource(ModelResource):
    by               = ToOneField(PersonResource, 'by')
    class Meta:
        cache = SimpleCache()
        queryset = Preapproval.objects.all()
        serializer = api.Serializer()
        #resource_name = 'preapproval'
        filtering = { 
            "id": ALL,
            "name": ALL,
            "time": ALL,
            "by": ALL_WITH_RELATIONS,
        }
api.submit.register(PreapprovalResource())

from ietf.group.resources import GroupResource
from ietf.name.resources import DraftSubmissionStateNameResource
from ietf.doc.resources import DocumentResource
class SubmissionResource(ModelResource):
    state            = ToOneField(DraftSubmissionStateNameResource, 'state')
    group            = ToOneField(GroupResource, 'group', null=True)
    draft            = ToOneField(DocumentResource, 'draft', null=True)
    class Meta:
        cache = SimpleCache()
        queryset = Submission.objects.all()
        serializer = api.Serializer()
        #resource_name = 'submission'
        filtering = { 
            "id": ALL,
            "remote_ip": ALL,
            "access_key": ALL,
            "auth_key": ALL,
            "name": ALL,
            "title": ALL,
            "abstract": ALL,
            "rev": ALL,
            "pages": ALL,
            "authors": ALL,
            "note": ALL,
            "replaces": ALL,
            "first_two_pages": ALL,
            "file_types": ALL,
            "file_size": ALL,
            "document_date": ALL,
            "submission_date": ALL,
            "submitter": ALL,
            "state": ALL_WITH_RELATIONS,
            "group": ALL_WITH_RELATIONS,
            "draft": ALL_WITH_RELATIONS,
        }
api.submit.register(SubmissionResource())

from ietf.person.resources import PersonResource
class SubmissionEventResource(ModelResource):
    submission       = ToOneField(SubmissionResource, 'submission')
    by               = ToOneField(PersonResource, 'by', null=True)
    class Meta:
        cache = SimpleCache()
        queryset = SubmissionEvent.objects.all()
        serializer = api.Serializer()
        #resource_name = 'submissionevent'
        filtering = { 
            "id": ALL,
            "time": ALL,
            "desc": ALL,
            "submission": ALL_WITH_RELATIONS,
            "by": ALL_WITH_RELATIONS,
        }
api.submit.register(SubmissionEventResource())

class SubmissionCheckResource(ModelResource):
    submission       = ToOneField(SubmissionResource, 'submission')
    class Meta:
        cache = SimpleCache()
        queryset = SubmissionCheck.objects.all()
        serializer = api.Serializer()
        #resource_name = 'submissioncheck'
        filtering = { 
            "id": ALL,
            "time": ALL,
            "checker": ALL,
            "passed": ALL,
            "message": ALL,
            "errors": ALL,
            "warnings": ALL,
            "items": ALL,
            "submission": ALL_WITH_RELATIONS,
        }
api.submit.register(SubmissionCheckResource())



from ietf.person.resources import PersonResource
from ietf.message.resources import MessageResource
class SubmissionEmailResource(ModelResource):
    submission       = ToOneField(SubmissionResource, 'submission')
    by               = ToOneField(PersonResource, 'by', null=True)
    submissionevent_ptr = ToOneField(SubmissionEventResource, 'submissionevent_ptr')
    message          = ToOneField(MessageResource, 'message', null=True)
    in_reply_to      = ToOneField(MessageResource, 'in_reply_to', null=True)
    class Meta:
        queryset = SubmissionEmail.objects.all()
        serializer = api.Serializer()
        cache = SimpleCache()
        #resource_name = 'submissionemail'
        filtering = { 
            "id": ALL,
            "time": ALL,
            "desc": ALL,
            "msgtype": ALL,
            "submission": ALL_WITH_RELATIONS,
            "by": ALL_WITH_RELATIONS,
            "submissionevent_ptr": ALL_WITH_RELATIONS,
            "message": ALL_WITH_RELATIONS,
            "in_reply_to": ALL_WITH_RELATIONS,
        }
api.submit.register(SubmissionEmailResource())

