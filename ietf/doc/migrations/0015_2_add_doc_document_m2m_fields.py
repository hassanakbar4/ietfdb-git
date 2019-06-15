# Copyright The IETF Trust 2019, All Rights Reserved
# -*- coding: utf-8 -*-
# Generated by Django 1.11.20 on 2019-05-28 12:42
from __future__ import unicode_literals

import sys, time

from django.db import migrations, models
import django.db.models.deletion
import ietf.utils.models


def timestamp(apps, schema_editor):
    sys.stderr.write('\n %s' % time.strftime('%Y-%m-%d %H:%M:%S'))

class Migration(migrations.Migration):

    dependencies = [
        ('name', '0006_adjust_statenames'),
        ('doc', '0015_1_add_fk_to_document_id'),
    ]

    operations = [
        migrations.CreateModel(
            name='DocumentLanguages',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('document', ietf.utils.models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='doc.Document', to_field='name', related_name='doclanguages')),
                ('formallanguagename', ietf.utils.models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='name.FormalLanguageName')),
            ],
        ),
        migrations.CreateModel(
            name='DocumentStates',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('document', ietf.utils.models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='doc.Document', to_field='name', related_name='docstates')),
                ('state', ietf.utils.models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='doc.State')),
            ],
        ),
        migrations.CreateModel(
            name='DocumentTags',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('document', ietf.utils.models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='doc.Document', to_field='name', related_name='doctags')),
                ('doctagname', ietf.utils.models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='name.DocTagName')),
            ],
        ),
        migrations.AddField(
            model_name='document',
            name='formal_languages2',
            field=models.ManyToManyField(blank=True, related_name='languagedocs', through='doc.DocumentLanguages', to='name.FormalLanguageName'),
        ),
        migrations.AddField(
            model_name='document',
            name='states2',
            field=models.ManyToManyField(blank=True, related_name='statedocs', through='doc.DocumentStates', to='doc.State'),
        ),
        migrations.AddField(
            model_name='document',
            name='tags2',
            field=models.ManyToManyField(blank=True, related_name='tagdocs', through='doc.DocumentTags', to='name.DocTagName'),
        ),
        # Here we copy the content of the existing implicit m2m tables for
        # the Document m2m fields into the explicit through tabeles, in order
        # to be able to later set the correct id from name
        migrations.RunPython(timestamp, timestamp),
        migrations.RunSQL(
            "INSERT INTO doc_documentlanguages SELECT * FROM doc_document_formal_languages;",
            ""),
        migrations.RunPython(timestamp, timestamp),
        migrations.RunSQL(
            "INSERT INTO doc_documentstates SELECT * FROM doc_document_states;",
            ""),
        migrations.RunPython(timestamp, timestamp),
        migrations.RunSQL(
            "INSERT INTO doc_documenttags SELECT * FROM doc_document_tags;",
            ""),
        migrations.RunPython(timestamp, timestamp),
        migrations.AddField(
            model_name='documentlanguages',
            name='document2',
            field=ietf.utils.models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='doc.Document', to_field='id', null=True, default=None),
        ),
        migrations.AddField(
            model_name='documentstates',
            name='document2',
            field=ietf.utils.models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='doc.Document', to_field='id', null=True, default=None),        ),
        migrations.AddField(
            model_name='documenttags',
            name='document2',
            field=ietf.utils.models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='doc.Document', to_field='id', null=True, default=None),

        ),
    ]
