# Copyright The IETF Trust 2016-2019, All Rights Reserved
# -*- coding: utf-8 -*-
# Autogenerated by the makeresources management command 2016-06-14 04:21 PDT


from tastypie.resources import ModelResource
from tastypie.fields import ToManyField                 # pyflakes:ignore
from tastypie.constants import ALL, ALL_WITH_RELATIONS  # pyflakes:ignore
from tastypie.cache import SimpleCache

from ietf import api
from ietf.api import ToOneField                         # pyflakes:ignore

from ietf.review.models import (ReviewerSettings, ReviewRequest, ReviewAssignment,
                                UnavailablePeriod, ReviewWish, NextReviewerInTeam,
                                ReviewSecretarySettings, ReviewTeamSettings, 
                                HistoricalReviewerSettings, HistoricalUnavailablePeriod,
                                HistoricalReviewRequest, HistoricalReviewAssignment)


from ietf.person.resources import PersonResource
from ietf.group.resources import GroupResource
class ReviewerSettingsResource(ModelResource):
    team             = ToOneField(GroupResource, 'team')
    person           = ToOneField(PersonResource, 'person')
    class Meta:
        queryset = ReviewerSettings.objects.all()
        serializer = api.Serializer()
        cache = SimpleCache()
        #resource_name = 'reviewer'
        ordering = ['id', ]
        filtering = { 
            "id": ALL,
            "min_interval": ALL,
            "filter_re": ALL,
            "skip_next": ALL,
            "team": ALL_WITH_RELATIONS,
            "person": ALL_WITH_RELATIONS,
        }
api.review.register(ReviewerSettingsResource())


from ietf.doc.resources import DocumentResource
from ietf.group.resources import GroupResource
from ietf.name.resources import ReviewRequestStateNameResource, ReviewTypeNameResource
from ietf.person.resources import PersonResource, EmailResource
class ReviewRequestResource(ModelResource):
    state            = ToOneField(ReviewRequestStateNameResource, 'state')
    type             = ToOneField(ReviewTypeNameResource, 'type')
    doc              = ToOneField(DocumentResource, 'doc')
    team             = ToOneField(GroupResource, 'team')
    requested_by     = ToOneField(PersonResource, 'requested_by')
    class Meta:
        queryset = ReviewRequest.objects.all()
        serializer = api.Serializer()
        cache = SimpleCache()
        #resource_name = 'reviewrequest'
        ordering = ['id', ]
        filtering = { 
            "id": ALL,
            "time": ALL,
            "deadline": ALL,
            "requested_rev": ALL,
            "comment": ALL,
            "state": ALL_WITH_RELATIONS,
            "type": ALL_WITH_RELATIONS,
            "doc": ALL_WITH_RELATIONS,
            "team": ALL_WITH_RELATIONS,
            "requested_by": ALL_WITH_RELATIONS,
        }
api.review.register(ReviewRequestResource())


class HistoricalReviewRequestResource(ModelResource):
    state            = ToOneField(ReviewRequestStateNameResource, 'state')
    type             = ToOneField(ReviewTypeNameResource, 'type')
    doc              = ToOneField(DocumentResource, 'doc')
    team             = ToOneField(GroupResource, 'team')
    requested_by     = ToOneField(PersonResource, 'requested_by')
    class Meta:
        queryset = HistoricalReviewRequest.objects.all()
        serializer = api.Serializer()
        cache = SimpleCache()
        #resource_name = 'reviewrequest'
        ordering = ['id', ]
        filtering = { 
            "id": ALL,
            "time": ALL,
            "deadline": ALL,
            "requested_rev": ALL,
            "comment": ALL,
            "state": ALL_WITH_RELATIONS,
            "type": ALL_WITH_RELATIONS,
            "doc": ALL_WITH_RELATIONS,
            "team": ALL_WITH_RELATIONS,
            "requested_by": ALL_WITH_RELATIONS,
        }
api.review.register(HistoricalReviewRequestResource())


from ietf.person.resources import PersonResource
from ietf.group.resources import GroupResource
class UnavailablePeriodResource(ModelResource):
    team             = ToOneField(GroupResource, 'team')
    person           = ToOneField(PersonResource, 'person')
    class Meta:
        queryset = UnavailablePeriod.objects.all()
        serializer = api.Serializer()
        cache = SimpleCache()
        #resource_name = 'unavailableperiod'
        ordering = ['id', ]
        filtering = { 
            "id": ALL,
            "start_date": ALL,
            "end_date": ALL,
            "availability": ALL,
            "reason": ALL,
            "team": ALL_WITH_RELATIONS,
            "person": ALL_WITH_RELATIONS,
        }
api.review.register(UnavailablePeriodResource())


class HistoricalUnavailablePeriodResource(ModelResource):
    team             = ToOneField(GroupResource, 'team')
    person           = ToOneField(PersonResource, 'person')
    class Meta:
        queryset = HistoricalUnavailablePeriod.objects.all()
        serializer = api.Serializer()
        cache = SimpleCache()
        ordering = ['id', ]
        filtering = { 
            "id": ALL,
            "start_date": ALL,
            "end_date": ALL,
            "availability": ALL,
            "reason": ALL,
            "team": ALL_WITH_RELATIONS,
            "person": ALL_WITH_RELATIONS,
        }
api.review.register(HistoricalUnavailablePeriodResource())


from ietf.person.resources import PersonResource
from ietf.group.resources import GroupResource
from ietf.doc.resources import DocumentResource
class ReviewWishResource(ModelResource):
    team             = ToOneField(GroupResource, 'team')
    person           = ToOneField(PersonResource, 'person')
    doc              = ToOneField(DocumentResource, 'doc')
    class Meta:
        queryset = ReviewWish.objects.all()
        serializer = api.Serializer()
        cache = SimpleCache()
        #resource_name = 'reviewwish'
        ordering = ['id', ]
        filtering = { 
            "id": ALL,
            "time": ALL,
            "team": ALL_WITH_RELATIONS,
            "person": ALL_WITH_RELATIONS,
            "doc": ALL_WITH_RELATIONS,
        }
api.review.register(ReviewWishResource())


from ietf.person.resources import PersonResource
from ietf.group.resources import GroupResource
class NextReviewerInTeamResource(ModelResource):
    team             = ToOneField(GroupResource, 'team')
    next_reviewer    = ToOneField(PersonResource, 'next_reviewer')
    class Meta:
        queryset = NextReviewerInTeam.objects.all()
        serializer = api.Serializer()
        cache = SimpleCache()
        #resource_name = 'nextreviewerinteam'
        ordering = ['id', ]
        filtering = { 
            "id": ALL,
            "team": ALL_WITH_RELATIONS,
            "next_reviewer": ALL_WITH_RELATIONS,
        }
api.review.register(NextReviewerInTeamResource())


from ietf.person.resources import PersonResource
from ietf.group.resources import GroupResource
class ReviewSecretarySettingsResource(ModelResource):
    team             = ToOneField(GroupResource, 'team')
    person           = ToOneField(PersonResource, 'person')
    class Meta:
        queryset = ReviewSecretarySettings.objects.all()
        serializer = api.Serializer()
        cache = SimpleCache()
        #resource_name = 'reviewsecretarysettings'
        ordering = ['id', ]
        filtering = { 
            "id": ALL,
            "remind_days_before_deadline": ALL,
            "team": ALL_WITH_RELATIONS,
            "person": ALL_WITH_RELATIONS,
        }
api.review.register(ReviewSecretarySettingsResource())


from ietf.group.resources import GroupResource
from ietf.name.resources import ReviewResultNameResource, ReviewTypeNameResource
class ReviewTeamSettingsResource(ModelResource):
    group            = ToOneField(GroupResource, 'group')
    review_types     = ToManyField(ReviewTypeNameResource, 'review_types', null=True)
    review_results   = ToManyField(ReviewResultNameResource, 'review_results', null=True)
    notify_ad_when   = ToManyField(ReviewResultNameResource, 'notify_ad_when', null = True)
    class Meta:
        queryset = ReviewTeamSettings.objects.all()
        serializer = api.Serializer()
        cache = SimpleCache()
        #resource_name = 'reviewteamsettings'
        ordering = ['id', ]
        filtering = { 
            "id": ALL,
            "autosuggest": ALL,
            "group": ALL_WITH_RELATIONS,
            "review_types": ALL_WITH_RELATIONS,
            "review_results": ALL_WITH_RELATIONS,
            "notify_ad_when": ALL_WITH_RELATIONS,
        }
api.review.register(ReviewTeamSettingsResource())


from ietf.person.resources import PersonResource
from ietf.group.resources import GroupResource
from ietf.utils.resources import UserResource
class HistoricalReviewerSettingsResource(ModelResource):
    team             = ToOneField(GroupResource, 'team', null=True)
    person           = ToOneField(PersonResource, 'person', null=True)
    history_user     = ToOneField(UserResource, 'history_user', null=True)
    class Meta:
        queryset = HistoricalReviewerSettings.objects.all()
        serializer = api.Serializer()
        cache = SimpleCache()
        #resource_name = 'historicalreviewersettings'
        ordering = ['id', ]
        filtering = { 
            "id": ALL,
            "min_interval": ALL,
            "filter_re": ALL,
            "skip_next": ALL,
            "remind_days_before_deadline": ALL,
            "expertise": ALL,
            "history_id": ALL,
            "history_change_reason": ALL,
            "history_date": ALL,
            "history_type": ALL,
            "team": ALL_WITH_RELATIONS,
            "person": ALL_WITH_RELATIONS,
            "history_user": ALL_WITH_RELATIONS,
        }
api.review.register(HistoricalReviewerSettingsResource())


from ietf.name.resources import ReviewAssignmentStateNameResource
class ReviewAssignmentResource(ModelResource):
    review_request   = ToOneField(ReviewRequestResource, 'review_request')
    state            = ToOneField(ReviewAssignmentStateNameResource, 'state')
    reviewer         = ToOneField(EmailResource, 'reviewer')
    review           = ToOneField(DocumentResource, 'review', null=True)
    result           = ToOneField(ReviewResultNameResource, 'result', null=True)
    class Meta:
        queryset = ReviewAssignment.objects.all()
        serializer = api.Serializer()
        cache = SimpleCache()
        #resource_name = 'reviewassignment'
        ordering = ['id', ]
        filtering = { 
            "id": ALL,
            "assigned_on": ALL,
            "completed_on": ALL,
            "reviewed_rev": ALL,
            "mailarch_url": ALL,
            "review_request": ALL_WITH_RELATIONS,
            "state": ALL_WITH_RELATIONS,
            "reviewer": ALL_WITH_RELATIONS,
            "review": ALL_WITH_RELATIONS,
            "result": ALL_WITH_RELATIONS,
        }
api.review.register(ReviewAssignmentResource())


class HistoricalReviewAssignmentResource(ModelResource):
    review_request   = ToOneField(ReviewRequestResource, 'review_request')
    state            = ToOneField(ReviewAssignmentStateNameResource, 'state')
    reviewer         = ToOneField(EmailResource, 'reviewer')
    review           = ToOneField(DocumentResource, 'review', null=True)
    result           = ToOneField(ReviewResultNameResource, 'result', null=True)
    class Meta:
        queryset = HistoricalReviewAssignment.objects.all()
        serializer = api.Serializer()
        cache = SimpleCache()
        #resource_name = 'reviewassignment'
        ordering = ['id', ]
        filtering = { 
            "id": ALL,
            "assigned_on": ALL,
            "completed_on": ALL,
            "reviewed_rev": ALL,
            "mailarch_url": ALL,
            "review_request": ALL_WITH_RELATIONS,
            "state": ALL_WITH_RELATIONS,
            "reviewer": ALL_WITH_RELATIONS,
            "review": ALL_WITH_RELATIONS,
            "result": ALL_WITH_RELATIONS,
        }
api.review.register(HistoricalReviewAssignmentResource())
