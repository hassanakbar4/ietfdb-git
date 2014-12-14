# Autogenerated by the mkresources management command 2014-11-13 23:53
from tastypie.resources import ModelResource
from tastypie.fields import ToOneField
from tastypie.constants import ALL, ALL_WITH_RELATIONS

from ietf import api

from ietf.ipr.models import *           # pyflakes:ignore


class IprDetailResource(ModelResource):
    class Meta:
        queryset = IprDetail.objects.all()
        #resource_name = 'iprdetail'
        filtering = { 
            "ipr_id": ALL,
            "title": ALL,
            "legacy_url_0": ALL,
            "legacy_url_1": ALL,
            "legacy_title_1": ALL,
            "legacy_url_2": ALL,
            "legacy_title_2": ALL,
            "legal_name": ALL,
            "rfc_number": ALL,
            "id_document_tag": ALL,
            "other_designations": ALL,
            "document_sections": ALL,
            "patents": ALL,
            "date_applied": ALL,
            "country": ALL,
            "notes": ALL,
            "is_pending": ALL,
            "applies_to_all": ALL,
            "licensing_option": ALL,
            "lic_opt_a_sub": ALL,
            "lic_opt_b_sub": ALL,
            "lic_opt_c_sub": ALL,
            "comments": ALL,
            "lic_checkbox": ALL,
            "other_notes": ALL,
            "third_party": ALL,
            "generic": ALL,
            "comply": ALL,
            "status": ALL,
            "submitted_date": ALL,
            "update_notified_date": ALL,
        }
api.ipr.register(IprDetailResource())

from ietf.doc.resources import DocAliasResource
class IprDocAliasResource(ModelResource):
    ipr              = ToOneField(IprDetailResource, 'ipr')
    doc_alias        = ToOneField(DocAliasResource, 'doc_alias')
    class Meta:
        queryset = IprDocAlias.objects.all()
        #resource_name = 'iprdocalias'
        filtering = { 
            "id": ALL,
            "rev": ALL,
            "ipr": ALL_WITH_RELATIONS,
            "doc_alias": ALL_WITH_RELATIONS,
        }
api.ipr.register(IprDocAliasResource())

class IprNotificationResource(ModelResource):
    ipr              = ToOneField(IprDetailResource, 'ipr')
    class Meta:
        queryset = IprNotification.objects.all()
        #resource_name = 'iprnotification'
        filtering = { 
            "id": ALL,
            "notification": ALL,
            "date_sent": ALL,
            "time_sent": ALL,
            "ipr": ALL_WITH_RELATIONS,
        }
api.ipr.register(IprNotificationResource())

class IprContactResource(ModelResource):
    ipr              = ToOneField(IprDetailResource, 'ipr')
    class Meta:
        queryset = IprContact.objects.all()
        #resource_name = 'iprcontact'
        filtering = { 
            "contact_id": ALL,
            "contact_type": ALL,
            "name": ALL,
            "title": ALL,
            "department": ALL,
            "address1": ALL,
            "address2": ALL,
            "telephone": ALL,
            "fax": ALL,
            "email": ALL,
            "ipr": ALL_WITH_RELATIONS,
        }
api.ipr.register(IprContactResource())

class IprUpdateResource(ModelResource):
    ipr              = ToOneField(IprDetailResource, 'ipr')
    updated          = ToOneField(IprDetailResource, 'updated')
    class Meta:
        queryset = IprUpdate.objects.all()
        #resource_name = 'iprupdate'
        filtering = { 
            "id": ALL,
            "status_to_be": ALL,
            "processed": ALL,
            "ipr": ALL_WITH_RELATIONS,
            "updated": ALL_WITH_RELATIONS,
        }
api.ipr.register(IprUpdateResource())

