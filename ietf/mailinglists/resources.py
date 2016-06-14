# Copyright The IETF Trust 2016, All Rights Reserved
# Autogenerated by the makeresources management command 2016-06-12 12:29 PDT
from tastypie.resources import ModelResource
from tastypie.fields import ToManyField                 # pyflakes:ignore
from tastypie.constants import ALL, ALL_WITH_RELATIONS  # pyflakes:ignore
from tastypie.cache import SimpleCache

from ietf import api
from ietf.api import ToOneField                         # pyflakes:ignore

from ietf.mailinglists.models import Whitelisted, List, Subscribed


from ietf.person.resources import PersonResource
class WhitelistedResource(ModelResource):
    by               = ToOneField(PersonResource, 'by')
    class Meta:
        queryset = Whitelisted.objects.all()
        serializer = api.Serializer()
        cache = SimpleCache()
        #resource_name = 'whitelisted'
        filtering = { 
            "id": ALL,
            "time": ALL,
            "address": ALL,
            "by": ALL_WITH_RELATIONS,
        }
api.mailinglists.register(WhitelistedResource())

class ListResource(ModelResource):
    class Meta:
        queryset = List.objects.all()
        serializer = api.Serializer()
        cache = SimpleCache()
        #resource_name = 'list'
        filtering = { 
            "id": ALL,
            "name": ALL,
            "description": ALL,
            "advertised": ALL,
        }
api.mailinglists.register(ListResource())

class SubscribedResource(ModelResource):
    lists            = ToManyField(ListResource, 'lists', null=True)
    class Meta:
        queryset = Subscribed.objects.all()
        serializer = api.Serializer()
        cache = SimpleCache()
        #resource_name = 'subscribed'
        filtering = { 
            "id": ALL,
            "time": ALL,
            "address": ALL,
            "lists": ALL_WITH_RELATIONS,
        }
api.mailinglists.register(SubscribedResource())

