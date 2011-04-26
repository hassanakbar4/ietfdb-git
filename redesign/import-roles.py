#!/usr/bin/python

import sys, os, re, datetime
import unaccent

basedir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path = [ basedir ] + sys.path

from ietf import settings
settings.USE_DB_REDESIGN_PROXY_CLASSES = False

from django.core import management
management.setup_environ(settings)

from redesign.person.models import *
from redesign.group.models import *
from redesign.name.models import *
from ietf.idtracker.models import IESGLogin, AreaDirector, IDAuthor, PersonOrOrgInfo, WGEditor, ChairsHistory, Role as OldRole

# assumptions:
#  - groups have been imported

# PersonOrOrgInfo/PostalAddress/EmailAddress/PhoneNumber are not
# imported, although some information is retrieved from those

# imports IESGLogin, AreaDirector, WGEditor, persons from IDAuthor,
# NomCom chairs from ChairsHistory

# should probably import WGChair, WGSecretary,
#  WGTechAdvisor, Role, IRTFChair

# make sure names exist
def name(name_class, slug, name, desc=""):
    # create if it doesn't exist, set name
    obj, _ = name_class.objects.get_or_create(slug=slug)
    obj.name = name
    obj.desc = desc
    obj.save()
    return obj

area_director_role = name(RoleName, "ad", "Area Director")
inactive_area_director_role = name(RoleName, "ex-ad", "Ex-Area Director", desc="Inactive Area Director")
wg_editor_role = name(RoleName, "wgeditor", "Working Group Editor")
chair_role = name(RoleName, "chair", "Chair")

# helpers for creating the objects
def get_or_create_email(o, create_fake):
    hardcoded_emails = { 'Dinara Suleymanova': "dinaras@ietf.org" }
    
    email = o.person.email()[1] or hardcoded_emails.get("%s %s" % (o.person.first_name, o.person.last_name))
    if not email:
        if create_fake:
            email = u"unknown-email-%s-%s" % (o.person.first_name, o.person.last_name)
            print ("USING FAKE EMAIL %s for %s %s %s" % (email, o.person.pk, o.person.first_name, o.person.last_name)).encode('utf-8')
        else:
            print ("NO EMAIL FOR %s %s %s %s %s" % (o.__class__, o.id, o.person.pk, o.person.first_name, o.person.last_name)).encode('utf-8')
            return None
    
    e, _ = Email.objects.get_or_create(address=email)
    if not e.person:
        n = u"%s %s" % (o.person.first_name, o.person.last_name)
        asciified = unaccent.asciify(n)
        aliases = Alias.objects.filter(name__in=(n, asciified))
        if aliases:
            p = aliases[0].person
        else:
            p = Person.objects.create(name=n, ascii=asciified)
            # FIXME: fill in address?
            Alias.objects.create(name=n, person=p)
            if asciified != n:
                Alias.objects.create(name=asciified, person=p)
        
        e.person = p
        e.save()

    return e

nomcom_groups = list(Group.objects.filter(acronym="nomcom"))
for o in ChairsHistory.objects.filter(chair_type=OldRole.NOMCOM_CHAIR):
    print "importing NOMCOM chair", o
    for g in nomcom_groups:
        if ("%s/%s" % (o.start_year, o.end_year)) in g.name:
            break

    email = get_or_create_email(o, create_fake=False)
    
    Role.objects.get_or_create(name=chair_role, group=g, email=email)

    
# IESGLogin
for o in IESGLogin.objects.all():
    print "importing IESGLogin", o.id, o.first_name, o.last_name
    
    if not o.person:
        persons = PersonOrOrgInfo.objects.filter(first_name=o.first_name, last_name=o.last_name)
        if persons:
            o.person = persons[0]
        else:
            print "NO PERSON", o.person_id
            continue

    email = get_or_create_email(o, create_fake=False)

    if o.user_level == IESGLogin.INACTIVE_AD_LEVEL:
        if not Role.objects.filter(name=inactive_area_director_role, email=email):
            # connect them directly to the IESG as we don't really know where they belong
            Role.objects.create(name=inactive_area_director_role, group=Group.objects.get(acronym="iesg"), email=email)
    
    # FIXME: import o.login_name, o.user_level
    
# AreaDirector
for o in AreaDirector.objects.all():
    if not o.area:
        print "NO AREA", o.person, o.area_id
        continue
    
    print "importing AreaDirector", o.area, o.person
    email = get_or_create_email(o, create_fake=False)
    
    area = Group.objects.get(acronym=o.area.area_acronym.acronym)

    if area.state_id == "active":
        role_type = area_director_role
    else:
         # can't be active area director in an inactive area
        role_type = inactive_area_director_role
    
    r = Role.objects.filter(name__in=(area_director_role, inactive_area_director_role),
                            email=email)
    if r and r[0].group == "iesg":
        r[0].group = area
        r[0].name = role_type
        r[0].save()
    else:
        Role.objects.get_or_create(name=role_type, group=area, email=email)

# WGEditor
for o in WGEditor.objects.all():
    # if not o.group_acronym:
    #     print "NO GROUP", o.person, o.group_acronym_id
    #     continue
    
    print "importing WGEditor", o.group_acronym, o.person
    email = get_or_create_email(o, create_fake=False)
    
    group = Group.objects.get(acronym=o.group_acronym.group_acronym.acronym)

    Role.objects.get_or_create(name=wg_editor_role, group=group, email=email)

# IDAuthor persons
for o in IDAuthor.objects.all().order_by('id').select_related('person'):
    print "importing IDAuthor", o.id, o.person_id, o.person.first_name.encode('utf-8'), o.person.last_name.encode('utf-8')
    email = get_or_create_email(o, create_fake=True)
    
