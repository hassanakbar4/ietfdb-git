# Copyright The IETF Trust 2020, All Rights Reserved
# -*- coding: utf-8 -*-
# Generated by Django 1.11.29 on 2020-03-19 13:06
from __future__ import unicode_literals

import re

import debug

from django.db import migrations

"""
This makes me very nervous:

>>> DocumentURL.objects.filter(desc__icontains='notifications').values_list('tag',flat=True).distinct()
<QuerySet ['yang-impact-analysis', 'yang-module-metadata']>

I suspect the wrong thing is happening with the map below wrt the GitHub notificaitons string.

"""

name_map = {
    "Issue.*":                "tracker",
    ".*FAQ.*":                "faq",
    ".*Area Web Page":        "webpage",
    ".*Wiki":                 "wiki",
    "Home Page":              "webpage",
    "Slack.*":                "slack",
    "Additional .* Web Page": "webpage",
    "Additional .* Page":     "webpage",
    "Yang catalog entry.*":   "yc_entry",
    "Yang impact analysis.*": "yc_impact",
    "GitHub":                 "github_repo",
    "Github page":            "github_repo",
    "GitHub repo.*":          "github_repo",
    "Github repository.*":    "github_repo",
    "GitHub notifications":   "github_notify",
    "GitHub org.*":           "github_org",
    "GitHub User.*":          "github_username",
    "GitLab User":            "gitlab_username",
    "GitLab User Name":       "gitlab_username",
}

def forward(apps, schema_editor):
    DocExtResource = apps.get_model('doc', 'DocExtResource')
    ExtResource = apps.get_model('extresource', 'ExtResource')
    ExtResourceName = apps.get_model('name', 'ExtResourceName')
    DocumentUrl = apps.get_model('doc', 'DocumentUrl')

    mapped = 0
    not_mapped = 0

    for doc_url in DocumentUrl.objects.all():
        match_found = False
        for regext,slug in name_map.items():
            if re.match(regext, doc_url.desc):
                match_found = True
                mapped += 1
                name = ExtResourceName.objects.get(slug=slug)
                ext_res = ExtResource.objects.create(name_id=slug, value= doc_url.url) # TODO: validate this value against name.type
                DocExtResource.objects.create(doc=doc_url.doc, extresource=ext_res)
                break
        if not match_found:
            debug.show('("Not Mapped:",doc_url.desc, doc_url.tag.slug, doc_url.doc.name, doc_url.url)')
            not_mapped += 1
    debug.show('(mapped, not_mapped)')

def reverse(apps, schema_editor):
    DocExtResource = apps.get_model('doc', 'DocExtResource')
    DocExtResource.objects.all().delete()

class Migration(migrations.Migration):

    dependencies = [
        ('doc', '0032_extres'),
        ('extresource', '0001_extres'),
        ('name', '0011_populate_extres'),
    ]

    operations = [
        migrations.RunPython(forward, reverse)
    ]
