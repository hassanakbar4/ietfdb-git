# Copyright The IETF Trust 2014-2019, All Rights Reserved
# -*- coding: utf-8 -*-
# Autogenerated by the mkresources management command 2014-11-13 23:53


from ietf.api import ModelResource
from tastypie.fields import ToOneField
from tastypie.constants import ALL, ALL_WITH_RELATIONS
from tastypie.cache import SimpleCache

from ietf import api

from ietf.person.models import (Person, Email, Alias, PersonalApiKey, PersonEvent, PersonApiKeyEvent, HistoricalPerson, HistoricalEmail)


from ietf.utils.resources import UserResource
class PersonResource(ModelResource):
    user             = ToOneField(UserResource, 'user', null=True)
    class Meta:
        cache = SimpleCache()
        queryset = Person.objects.all()
        serializer = api.Serializer()
        #resource_name = 'person'
        ordering = ['id', ]
        filtering = { 
            "id": ALL,
            "time": ALL,
            "name": ALL,
            "ascii": ALL,
            "ascii_short": ALL,
            "affiliation": ALL,
            "photo": ALL,
            "biography": ALL,
            "user": ALL_WITH_RELATIONS,
        }
api.person.register(PersonResource())

class EmailResource(ModelResource):
    person           = ToOneField(PersonResource, 'person', null=True)
    class Meta:
        cache = SimpleCache()
        queryset = Email.objects.all()
        serializer = api.Serializer()
        #resource_name = 'email'
        ordering = ['address', ]
        filtering = { 
            "address": ALL,
            "time": ALL,
            "active": ALL,
            "person": ALL_WITH_RELATIONS,
        }
api.person.register(EmailResource())

class AliasResource(ModelResource):
    person           = ToOneField(PersonResource, 'person')
    class Meta:
        cache = SimpleCache()
        queryset = Alias.objects.all()
        serializer = api.Serializer()
        #resource_name = 'alias'
        ordering = ['id', ]
        filtering = { 
            "id": ALL,
            "name": ALL,
            "person": ALL_WITH_RELATIONS,
        }
api.person.register(AliasResource())

class PersonalApiKeyResource(ModelResource):
    person           = ToOneField(PersonResource, 'person')
    class Meta:
        queryset = PersonalApiKey.objects.all()
        serializer = api.Serializer()
        cache = SimpleCache()
        excludes = ['salt', ]
        #resource_name = 'personalapikey'
        ordering = ['id', ]
        filtering = { 
            "id": ALL,
            "endpoint": ALL,
            "created": ALL,
            "valid": ALL,
            "salt": ALL,
            "count": ALL,
            "latest": ALL,
            "person": ALL_WITH_RELATIONS,
        }
api.person.register(PersonalApiKeyResource())


class PersonEventResource(ModelResource):
    person           = ToOneField(PersonResource, 'person')
    class Meta:
        queryset = PersonEvent.objects.all()
        serializer = api.Serializer()
        cache = SimpleCache()
        #resource_name = 'personevent'
        ordering = ['id', ]
        filtering = { 
            "id": ALL,
            "time": ALL,
            "type": ALL,
            "desc": ALL,
            "person": ALL_WITH_RELATIONS,
        }
api.person.register(PersonEventResource())


class PersonApiKeyEventResource(ModelResource):
    person           = ToOneField(PersonResource, 'person')
    personevent_ptr  = ToOneField(PersonEventResource, 'personevent_ptr')
    key              = ToOneField(PersonalApiKeyResource, 'key')
    class Meta:
        queryset = PersonApiKeyEvent.objects.all()
        serializer = api.Serializer()
        cache = SimpleCache()
        #resource_name = 'personapikeyevent'
        ordering = ['id', ]
        filtering = { 
            "id": ALL,
            "time": ALL,
            "type": ALL,
            "desc": ALL,
            "person": ALL_WITH_RELATIONS,
            "personevent_ptr": ALL_WITH_RELATIONS,
            "key": ALL_WITH_RELATIONS,
        }
api.person.register(PersonApiKeyEventResource())


from ietf.utils.resources import UserResource
class HistoricalPersonResource(ModelResource):
    user             = ToOneField(UserResource, 'user', null=True)
    history_user     = ToOneField(UserResource, 'history_user', null=True)
    class Meta:
        queryset = HistoricalPerson.objects.all()
        serializer = api.Serializer()
        cache = SimpleCache()
        #resource_name = 'historicalperson'
        ordering = ['id', ]
        filtering = { 
            "id": ALL,
            "time": ALL,
            "name": ALL,
            "ascii": ALL,
            "ascii_short": ALL,
            "affiliation": ALL,
            "biography": ALL,
            "photo": ALL,
            "photo_thumb": ALL,
            "history_id": ALL,
            "history_date": ALL,
            "history_change_reason": ALL,
            "history_type": ALL,
            "user": ALL_WITH_RELATIONS,
            "history_user": ALL_WITH_RELATIONS,
        }
api.person.register(HistoricalPersonResource())


from ietf.utils.resources import UserResource
class HistoricalEmailResource(ModelResource):
    person           = ToOneField(PersonResource, 'person', null=True)
    history_user     = ToOneField(UserResource, 'history_user', null=True)
    class Meta:
        queryset = HistoricalEmail.objects.all()
        serializer = api.Serializer()
        cache = SimpleCache()
        #resource_name = 'historicalemail'
        ordering = ['id', ]
        filtering = { 
            "address": ALL,
            "time": ALL,
            "primary": ALL,
            "origin": ALL,
            "active": ALL,
            "history_id": ALL,
            "history_date": ALL,
            "history_change_reason": ALL,
            "history_type": ALL,
            "person": ALL_WITH_RELATIONS,
            "history_user": ALL_WITH_RELATIONS,
        }
api.person.register(HistoricalEmailResource())
