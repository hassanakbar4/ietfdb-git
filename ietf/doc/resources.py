# Autogenerated by the makeresources management command 2015-10-19 12:29 PDT
from ietf.api import ModelResource
from ietf.api import ToOneField
from tastypie.fields import ToManyField, CharField
from tastypie.constants import ALL, ALL_WITH_RELATIONS # pyflakes:ignore
from tastypie.cache import SimpleCache

from ietf import api

from ietf.doc.models import (BallotType, DeletedEvent, StateType, State, Document,
    DocumentAuthor, DocEvent, StateDocEvent, DocHistory, ConsensusDocEvent, DocAlias,
    TelechatDocEvent, DocReminder, LastCallDocEvent, NewRevisionDocEvent, WriteupDocEvent,
    InitialReviewDocEvent, DocHistoryAuthor, BallotDocEvent, RelatedDocument,
    RelatedDocHistory, BallotPositionDocEvent, AddedMessageEvent, SubmissionDocEvent,
    ReviewRequestDocEvent)

from ietf.name.resources import BallotPositionNameResource, DocTypeNameResource
class BallotTypeResource(ModelResource):
    doc_type         = ToOneField(DocTypeNameResource, 'doc_type', null=True)
    positions        = ToManyField(BallotPositionNameResource, 'positions', null=True)
    class Meta:
        cache = SimpleCache()
        queryset = BallotType.objects.all()
        serializer = api.Serializer()
        #resource_name = 'ballottype'
        filtering = { 
            "id": ALL,
            "slug": ALL,
            "name": ALL,
            "question": ALL,
            "used": ALL,
            "order": ALL,
            "doc_type": ALL_WITH_RELATIONS,
            "positions": ALL_WITH_RELATIONS,
        }
api.doc.register(BallotTypeResource())

from ietf.person.resources import PersonResource
from ietf.utils.resources import ContentTypeResource
class DeletedEventResource(ModelResource):
    content_type     = ToOneField(ContentTypeResource, 'content_type')
    by               = ToOneField(PersonResource, 'by')
    class Meta:
        cache = SimpleCache()
        queryset = DeletedEvent.objects.all()
        serializer = api.Serializer()
        #resource_name = 'deletedevent'
        filtering = { 
            "id": ALL,
            "json": ALL,
            "time": ALL,
            "content_type": ALL_WITH_RELATIONS,
            "by": ALL_WITH_RELATIONS,
        }
api.doc.register(DeletedEventResource())

class StateTypeResource(ModelResource):
    class Meta:
        cache = SimpleCache()
        queryset = StateType.objects.all()
        serializer = api.Serializer()
        #resource_name = 'statetype'
        filtering = { 
            "slug": ALL,
            "label": ALL,
        }
api.doc.register(StateTypeResource())

class StateResource(ModelResource):
    type             = ToOneField(StateTypeResource, 'type')
    next_states      = ToManyField('ietf.doc.resources.StateResource', 'next_states', null=True)
    class Meta:
        cache = SimpleCache()
        queryset = State.objects.all()
        serializer = api.Serializer()
        #resource_name = 'state'
        filtering = { 
            "id": ALL,
            "slug": ALL,
            "name": ALL,
            "used": ALL,
            "desc": ALL,
            "order": ALL,
            "type": ALL_WITH_RELATIONS,
            "next_states": ALL_WITH_RELATIONS,
        }
api.doc.register(StateResource())

from ietf.person.resources import PersonResource, EmailResource
from ietf.group.resources import GroupResource
from ietf.name.resources import StdLevelNameResource, StreamNameResource, DocTypeNameResource, DocTagNameResource, IntendedStdLevelNameResource
class DocumentResource(ModelResource):
    type             = ToOneField(DocTypeNameResource, 'type', null=True)
    stream           = ToOneField(StreamNameResource, 'stream', null=True)
    group            = ToOneField(GroupResource, 'group', null=True)
    intended_std_level = ToOneField(IntendedStdLevelNameResource, 'intended_std_level', null=True)
    std_level        = ToOneField(StdLevelNameResource, 'std_level', null=True)
    ad               = ToOneField(PersonResource, 'ad', null=True)
    shepherd         = ToOneField(EmailResource, 'shepherd', null=True)
    states           = ToManyField(StateResource, 'states', null=True)
    tags             = ToManyField(DocTagNameResource, 'tags', null=True)
    authors          = ToManyField(EmailResource, 'authors', null=True)
    rfc              = CharField(attribute='rfc_number', null=True)
    class Meta:
        cache = SimpleCache()
        queryset = Document.objects.all()
        serializer = api.Serializer()
        #resource_name = 'document'
        filtering = { 
            "time": ALL,
            "title": ALL,
            "abstract": ALL,
            "rev": ALL,
            "pages": ALL,
            "order": ALL,
            "expires": ALL,
            "notify": ALL,
            "external_url": ALL,
            "note": ALL,
            "internal_comments": ALL,
            "name": ALL,
            "type": ALL_WITH_RELATIONS,
            "stream": ALL_WITH_RELATIONS,
            "group": ALL_WITH_RELATIONS,
            "intended_std_level": ALL_WITH_RELATIONS,
            "std_level": ALL_WITH_RELATIONS,
            "ad": ALL_WITH_RELATIONS,
            "shepherd": ALL_WITH_RELATIONS,
            "states": ALL_WITH_RELATIONS,
            "tags": ALL_WITH_RELATIONS,
            "authors": ALL_WITH_RELATIONS,
        }
api.doc.register(DocumentResource())

from ietf.person.resources import EmailResource
class DocumentAuthorResource(ModelResource):
    document         = ToOneField(DocumentResource, 'document')
    author           = ToOneField(EmailResource, 'author')
    class Meta:
        cache = SimpleCache()
        queryset = DocumentAuthor.objects.all()
        serializer = api.Serializer()
        #resource_name = 'documentauthor'
        filtering = { 
            "id": ALL,
            "order": ALL,
            "document": ALL_WITH_RELATIONS,
            "author": ALL_WITH_RELATIONS,
        }
api.doc.register(DocumentAuthorResource())

from ietf.person.resources import PersonResource
class DocEventResource(ModelResource):
    by               = ToOneField(PersonResource, 'by')
    doc              = ToOneField(DocumentResource, 'doc')
    class Meta:
        cache = SimpleCache()
        queryset = DocEvent.objects.all()
        serializer = api.Serializer()
        #resource_name = 'docevent'
        filtering = { 
            "id": ALL,
            "time": ALL,
            "type": ALL,
            "rev": ALL,
            "desc": ALL,
            "by": ALL_WITH_RELATIONS,
            "doc": ALL_WITH_RELATIONS,
        }
api.doc.register(DocEventResource())

from ietf.person.resources import PersonResource
class StateDocEventResource(ModelResource):
    by               = ToOneField(PersonResource, 'by')
    doc              = ToOneField(DocumentResource, 'doc')
    docevent_ptr     = ToOneField(DocEventResource, 'docevent_ptr')
    state_type       = ToOneField(StateTypeResource, 'state_type')
    state            = ToOneField(StateResource, 'state', null=True)
    class Meta:
        cache = SimpleCache()
        queryset = StateDocEvent.objects.all()
        serializer = api.Serializer()
        #resource_name = 'statedocevent'
        filtering = { 
            "id": ALL,
            "time": ALL,
            "type": ALL,
            "rev": ALL,
            "desc": ALL,
            "by": ALL_WITH_RELATIONS,
            "doc": ALL_WITH_RELATIONS,
            "docevent_ptr": ALL_WITH_RELATIONS,
            "state_type": ALL_WITH_RELATIONS,
            "state": ALL_WITH_RELATIONS,
        }
api.doc.register(StateDocEventResource())

from ietf.person.resources import PersonResource, EmailResource
from ietf.group.resources import GroupResource
from ietf.name.resources import StdLevelNameResource, StreamNameResource, DocTypeNameResource, DocTagNameResource, IntendedStdLevelNameResource
class DocHistoryResource(ModelResource):
    type             = ToOneField(DocTypeNameResource, 'type', null=True)
    stream           = ToOneField(StreamNameResource, 'stream', null=True)
    group            = ToOneField(GroupResource, 'group', null=True)
    intended_std_level = ToOneField(IntendedStdLevelNameResource, 'intended_std_level', null=True)
    std_level        = ToOneField(StdLevelNameResource, 'std_level', null=True)
    ad               = ToOneField(PersonResource, 'ad', null=True)
    shepherd         = ToOneField(EmailResource, 'shepherd', null=True)
    doc              = ToOneField(DocumentResource, 'doc')
    states           = ToManyField(StateResource, 'states', null=True)
    tags             = ToManyField(DocTagNameResource, 'tags', null=True)
    authors          = ToManyField(EmailResource, 'authors', null=True)
    class Meta:
        cache = SimpleCache()
        queryset = DocHistory.objects.all()
        serializer = api.Serializer()
        #resource_name = 'dochistory'
        filtering = { 
            "id": ALL,
            "time": ALL,
            "title": ALL,
            "abstract": ALL,
            "rev": ALL,
            "pages": ALL,
            "order": ALL,
            "expires": ALL,
            "notify": ALL,
            "external_url": ALL,
            "note": ALL,
            "internal_comments": ALL,
            "name": ALL,
            "type": ALL_WITH_RELATIONS,
            "stream": ALL_WITH_RELATIONS,
            "group": ALL_WITH_RELATIONS,
            "intended_std_level": ALL_WITH_RELATIONS,
            "std_level": ALL_WITH_RELATIONS,
            "ad": ALL_WITH_RELATIONS,
            "shepherd": ALL_WITH_RELATIONS,
            "doc": ALL_WITH_RELATIONS,
            "states": ALL_WITH_RELATIONS,
            "tags": ALL_WITH_RELATIONS,
            "authors": ALL_WITH_RELATIONS,
        }
api.doc.register(DocHistoryResource())

from ietf.person.resources import PersonResource
class ConsensusDocEventResource(ModelResource):
    by               = ToOneField(PersonResource, 'by')
    doc              = ToOneField(DocumentResource, 'doc')
    docevent_ptr     = ToOneField(DocEventResource, 'docevent_ptr')
    class Meta:
        cache = SimpleCache()
        queryset = ConsensusDocEvent.objects.all()
        serializer = api.Serializer()
        #resource_name = 'consensusdocevent'
        filtering = { 
            "id": ALL,
            "time": ALL,
            "type": ALL,
            "rev": ALL,
            "desc": ALL,
            "consensus": ALL,
            "by": ALL_WITH_RELATIONS,
            "doc": ALL_WITH_RELATIONS,
            "docevent_ptr": ALL_WITH_RELATIONS,
        }
api.doc.register(ConsensusDocEventResource())

class DocAliasResource(ModelResource):
    document         = ToOneField(DocumentResource, 'document')
    class Meta:
        cache = SimpleCache()
        queryset = DocAlias.objects.all()
        serializer = api.Serializer()
        #resource_name = 'docalias'
        filtering = { 
            "name": ALL,
            "document": ALL_WITH_RELATIONS,
        }
api.doc.register(DocAliasResource())

from ietf.person.resources import PersonResource
class TelechatDocEventResource(ModelResource):
    by               = ToOneField(PersonResource, 'by')
    doc              = ToOneField(DocumentResource, 'doc')
    docevent_ptr     = ToOneField(DocEventResource, 'docevent_ptr')
    class Meta:
        cache = SimpleCache()
        queryset = TelechatDocEvent.objects.all()
        serializer = api.Serializer()
        #resource_name = 'telechatdocevent'
        filtering = { 
            "id": ALL,
            "time": ALL,
            "type": ALL,
            "rev": ALL,
            "desc": ALL,
            "telechat_date": ALL,
            "returning_item": ALL,
            "by": ALL_WITH_RELATIONS,
            "doc": ALL_WITH_RELATIONS,
            "docevent_ptr": ALL_WITH_RELATIONS,
        }
api.doc.register(TelechatDocEventResource())

from ietf.name.resources import DocReminderTypeNameResource
class DocReminderResource(ModelResource):
    event            = ToOneField(DocEventResource, 'event')
    type             = ToOneField(DocReminderTypeNameResource, 'type')
    class Meta:
        cache = SimpleCache()
        queryset = DocReminder.objects.all()
        serializer = api.Serializer()
        #resource_name = 'docreminder'
        filtering = { 
            "id": ALL,
            "due": ALL,
            "active": ALL,
            "event": ALL_WITH_RELATIONS,
            "type": ALL_WITH_RELATIONS,
        }
api.doc.register(DocReminderResource())

from ietf.person.resources import PersonResource
class LastCallDocEventResource(ModelResource):
    by               = ToOneField(PersonResource, 'by')
    doc              = ToOneField(DocumentResource, 'doc')
    docevent_ptr     = ToOneField(DocEventResource, 'docevent_ptr')
    class Meta:
        cache = SimpleCache()
        queryset = LastCallDocEvent.objects.all()
        serializer = api.Serializer()
        #resource_name = 'lastcalldocevent'
        filtering = { 
            "id": ALL,
            "time": ALL,
            "type": ALL,
            "rev": ALL,
            "desc": ALL,
            "expires": ALL,
            "by": ALL_WITH_RELATIONS,
            "doc": ALL_WITH_RELATIONS,
            "docevent_ptr": ALL_WITH_RELATIONS,
        }
api.doc.register(LastCallDocEventResource())

from ietf.person.resources import PersonResource
class NewRevisionDocEventResource(ModelResource):
    by               = ToOneField(PersonResource, 'by')
    doc              = ToOneField(DocumentResource, 'doc')
    docevent_ptr     = ToOneField(DocEventResource, 'docevent_ptr')
    class Meta:
        cache = SimpleCache()
        queryset = NewRevisionDocEvent.objects.all()
        serializer = api.Serializer()
        #resource_name = 'newrevisiondocevent'
        filtering = { 
            "id": ALL,
            "time": ALL,
            "type": ALL,
            "desc": ALL,
            "rev": ALL,
            "by": ALL_WITH_RELATIONS,
            "doc": ALL_WITH_RELATIONS,
            "docevent_ptr": ALL_WITH_RELATIONS,
        }
api.doc.register(NewRevisionDocEventResource())

from ietf.person.resources import PersonResource
class WriteupDocEventResource(ModelResource):
    by               = ToOneField(PersonResource, 'by')
    doc              = ToOneField(DocumentResource, 'doc')
    docevent_ptr     = ToOneField(DocEventResource, 'docevent_ptr')
    class Meta:
        cache = SimpleCache()
        queryset = WriteupDocEvent.objects.all()
        serializer = api.Serializer()
        #resource_name = 'writeupdocevent'
        filtering = { 
            "id": ALL,
            "time": ALL,
            "type": ALL,
            "rev": ALL,
            "desc": ALL,
            "text": ALL,
            "by": ALL_WITH_RELATIONS,
            "doc": ALL_WITH_RELATIONS,
            "docevent_ptr": ALL_WITH_RELATIONS,
        }
api.doc.register(WriteupDocEventResource())

from ietf.person.resources import PersonResource
class InitialReviewDocEventResource(ModelResource):
    by               = ToOneField(PersonResource, 'by')
    doc              = ToOneField(DocumentResource, 'doc')
    docevent_ptr     = ToOneField(DocEventResource, 'docevent_ptr')
    class Meta:
        cache = SimpleCache()
        queryset = InitialReviewDocEvent.objects.all()
        serializer = api.Serializer()
        #resource_name = 'initialreviewdocevent'
        filtering = { 
            "id": ALL,
            "time": ALL,
            "type": ALL,
            "rev": ALL,
            "desc": ALL,
            "expires": ALL,
            "by": ALL_WITH_RELATIONS,
            "doc": ALL_WITH_RELATIONS,
            "docevent_ptr": ALL_WITH_RELATIONS,
        }
api.doc.register(InitialReviewDocEventResource())

from ietf.person.resources import EmailResource
class DocHistoryAuthorResource(ModelResource):
    document         = ToOneField(DocHistoryResource, 'document')
    author           = ToOneField(EmailResource, 'author')
    class Meta:
        cache = SimpleCache()
        queryset = DocHistoryAuthor.objects.all()
        serializer = api.Serializer()
        #resource_name = 'dochistoryauthor'
        filtering = { 
            "id": ALL,
            "order": ALL,
            "document": ALL_WITH_RELATIONS,
            "author": ALL_WITH_RELATIONS,
        }
api.doc.register(DocHistoryAuthorResource())

from ietf.person.resources import PersonResource
class BallotDocEventResource(ModelResource):
    by               = ToOneField(PersonResource, 'by')
    doc              = ToOneField(DocumentResource, 'doc')
    docevent_ptr     = ToOneField(DocEventResource, 'docevent_ptr')
    ballot_type      = ToOneField(BallotTypeResource, 'ballot_type')
    class Meta:
        cache = SimpleCache()
        queryset = BallotDocEvent.objects.all()
        serializer = api.Serializer()
        #resource_name = 'ballotdocevent'
        filtering = { 
            "id": ALL,
            "time": ALL,
            "type": ALL,
            "rev": ALL,
            "desc": ALL,
            "by": ALL_WITH_RELATIONS,
            "doc": ALL_WITH_RELATIONS,
            "docevent_ptr": ALL_WITH_RELATIONS,
            "ballot_type": ALL_WITH_RELATIONS,
        }
api.doc.register(BallotDocEventResource())

from ietf.name.resources import DocRelationshipNameResource
class RelatedDocumentResource(ModelResource):
    source           = ToOneField(DocumentResource, 'source')
    target           = ToOneField(DocAliasResource, 'target')
    relationship     = ToOneField(DocRelationshipNameResource, 'relationship')
    class Meta:
        cache = SimpleCache()
        queryset = RelatedDocument.objects.all()
        serializer = api.Serializer()
        #resource_name = 'relateddocument'
        filtering = { 
            "id": ALL,
            "source": ALL_WITH_RELATIONS,
            "target": ALL_WITH_RELATIONS,
            "relationship": ALL_WITH_RELATIONS,
        }
api.doc.register(RelatedDocumentResource())

from ietf.name.resources import DocRelationshipNameResource
class RelatedDocHistoryResource(ModelResource):
    source           = ToOneField(DocHistoryResource, 'source')
    target           = ToOneField(DocAliasResource, 'target')
    relationship     = ToOneField(DocRelationshipNameResource, 'relationship')
    class Meta:
        cache = SimpleCache()
        queryset = RelatedDocHistory.objects.all()
        serializer = api.Serializer()
        #resource_name = 'relateddochistory'
        filtering = { 
            "id": ALL,
            "source": ALL_WITH_RELATIONS,
            "target": ALL_WITH_RELATIONS,
            "relationship": ALL_WITH_RELATIONS,
        }
api.doc.register(RelatedDocHistoryResource())

from ietf.person.resources import PersonResource
from ietf.name.resources import BallotPositionNameResource
class BallotPositionDocEventResource(ModelResource):
    by               = ToOneField(PersonResource, 'by')
    doc              = ToOneField(DocumentResource, 'doc')
    docevent_ptr     = ToOneField(DocEventResource, 'docevent_ptr')
    ballot           = ToOneField(BallotDocEventResource, 'ballot', null=True)
    ad               = ToOneField(PersonResource, 'ad')
    pos              = ToOneField(BallotPositionNameResource, 'pos')
    class Meta:
        cache = SimpleCache()
        queryset = BallotPositionDocEvent.objects.all()
        serializer = api.Serializer()
        #resource_name = 'ballotpositiondocevent'
        filtering = { 
            "id": ALL,
            "time": ALL,
            "type": ALL,
            "rev": ALL,
            "desc": ALL,
            "discuss": ALL,
            "discuss_time": ALL,
            "comment": ALL,
            "comment_time": ALL,
            "by": ALL_WITH_RELATIONS,
            "doc": ALL_WITH_RELATIONS,
            "docevent_ptr": ALL_WITH_RELATIONS,
            "ballot": ALL_WITH_RELATIONS,
            "ad": ALL_WITH_RELATIONS,
            "pos": ALL_WITH_RELATIONS,
        }
api.doc.register(BallotPositionDocEventResource())

from ietf.person.resources import PersonResource
from ietf.message.resources import MessageResource
class AddedMessageEventResource(ModelResource):
    by               = ToOneField(PersonResource, 'by')
    doc              = ToOneField(DocumentResource, 'doc')
    docevent_ptr     = ToOneField(DocEventResource, 'docevent_ptr')
    message          = ToOneField(MessageResource, 'message', null=True)
    in_reply_to      = ToOneField(MessageResource, 'in_reply_to', null=True)
    class Meta:
        queryset = AddedMessageEvent.objects.all()
        serializer = api.Serializer()
        cache = SimpleCache()
        #resource_name = 'addedmessageevent'
        filtering = { 
            "id": ALL,
            "time": ALL,
            "type": ALL,
            "rev": ALL,
            "desc": ALL,
            "msgtype": ALL,
            "by": ALL_WITH_RELATIONS,
            "doc": ALL_WITH_RELATIONS,
            "docevent_ptr": ALL_WITH_RELATIONS,
            "message": ALL_WITH_RELATIONS,
            "in_reply_to": ALL_WITH_RELATIONS,
        }
api.doc.register(AddedMessageEventResource())

from ietf.person.resources import PersonResource
from ietf.submit.resources import SubmissionResource
class SubmissionDocEventResource(ModelResource):
    by               = ToOneField(PersonResource, 'by')
    doc              = ToOneField(DocumentResource, 'doc')
    docevent_ptr     = ToOneField(DocEventResource, 'docevent_ptr')
    submission       = ToOneField(SubmissionResource, 'submission')
    class Meta:
        queryset = SubmissionDocEvent.objects.all()
        serializer = api.Serializer()
        cache = SimpleCache()
        #resource_name = 'submissiondocevent'
        filtering = { 
            "id": ALL,
            "time": ALL,
            "type": ALL,
            "desc": ALL,
            "rev": ALL,
            "by": ALL_WITH_RELATIONS,
            "doc": ALL_WITH_RELATIONS,
            "docevent_ptr": ALL_WITH_RELATIONS,
            "submission": ALL_WITH_RELATIONS,
        }
api.doc.register(SubmissionDocEventResource())

from ietf.person.resources import PersonResource
from ietf.name.resources import ReviewRequestStateNameResource
class ReviewRequestDocEventResource(ModelResource):
    by               = ToOneField(PersonResource, 'by')
    doc              = ToOneField(DocumentResource, 'doc')
    docevent_ptr     = ToOneField(DocEventResource, 'docevent_ptr')
    review_request   = ToOneField('ietf.review.resources.ReviewRequestResource', 'review_request')
    state            = ToOneField(ReviewRequestStateNameResource, 'state', null=True)
    class Meta:
        queryset = ReviewRequestDocEvent.objects.all()
        serializer = api.Serializer()
        cache = SimpleCache()
        #resource_name = 'reviewrequestdocevent'
        filtering = { 
            "id": ALL,
            "time": ALL,
            "type": ALL,
            "rev": ALL,
            "desc": ALL,
            "by": ALL_WITH_RELATIONS,
            "doc": ALL_WITH_RELATIONS,
            "docevent_ptr": ALL_WITH_RELATIONS,
            "review_request": ALL_WITH_RELATIONS,
            "state": ALL_WITH_RELATIONS,
        }
api.doc.register(ReviewRequestDocEventResource())

