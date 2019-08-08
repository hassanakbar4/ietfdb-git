# Copyright The IETF Trust 2018-2019, All Rights Reserved
# -*- coding: utf-8 -*-
# Generated by Django 1.11.13 on 2018-07-10 15:58


from __future__ import absolute_import, print_function, unicode_literals

import django.core.validators
import django.db.models.deletion

from django.conf import settings
from django.db import migrations, models


import debug                            # pyflakes:ignore

import ietf.utils.models

class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('name', '0002_agendatypename'),
        ('group', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='GroupFeatures',
            fields=[
                ('type', ietf.utils.models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, primary_key=True, serialize=False, to='name.GroupTypeName', related_name='features')),
                ('has_milestones', models.BooleanField(default=False, verbose_name='Milestones')),
                ('has_chartering_process', models.BooleanField(default=False, verbose_name='Chartering')),
                ('has_documents', models.BooleanField(default=False, verbose_name='Documents')),
                ('has_dependencies', models.BooleanField(default=False, verbose_name='Dependencies')),
                ('has_nonsession_materials', models.BooleanField(default=False, verbose_name='Materials')),
                ('has_meetings', models.BooleanField(default=False, verbose_name='Meetings')),
                ('has_reviews', models.BooleanField(default=False, verbose_name='Reviews')),
                ('has_default_jabber', models.BooleanField(default=False, verbose_name='Jabber')),
                ('customize_workflow', models.BooleanField(default=False, verbose_name='Workflow')),
                ('about_page', models.CharField(default='ietf.group.views.group_about', max_length=64)),
                ('default_tab', models.CharField(default='ietf.group.views.group_about', max_length=64)),
                ('material_types', models.CharField(default='slides', max_length=64, validators=[django.core.validators.RegexValidator(code=b'invalid', message=b'Enter a comma-separated list of material types', regex=b'[a-z0-9_-]+(,[a-z0-9_-]+)*')])),
                ('admin_roles', models.CharField(default='chair', max_length=64, validators=[django.core.validators.RegexValidator(code=b'invalid', message=b'Enter a comma-separated list of role slugs', regex=b'[a-z0-9_-]+(,[a-z0-9_-]+)*')])),
                ('agenda_type', models.ForeignKey(default='ietf', null=True, on_delete=django.db.models.deletion.CASCADE, to='name.AgendaTypeName')),
            ],
        ),
        migrations.CreateModel(
            name='HistoricalGroupFeatures',
            fields=[
                ('has_milestones', models.BooleanField(default=False, verbose_name='Milestones')),
                ('has_chartering_process', models.BooleanField(default=False, verbose_name='Chartering')),
                ('has_documents', models.BooleanField(default=False, verbose_name='Documents')),
                ('has_dependencies', models.BooleanField(default=False, verbose_name='Dependencies')),
                ('has_nonsession_materials', models.BooleanField(default=False, verbose_name='Materials')),
                ('has_meetings', models.BooleanField(default=False, verbose_name='Meetings')),
                ('has_reviews', models.BooleanField(default=False, verbose_name='Reviews')),
                ('has_default_jabber', models.BooleanField(default=False, verbose_name='Jabber')),
                ('customize_workflow', models.BooleanField(default=False, verbose_name='Workflow')),
                ('about_page', models.CharField(default='ietf.group.views.group_about', max_length=64)),
                ('default_tab', models.CharField(default='ietf.group.views.group_about', max_length=64)),
                ('material_types', models.CharField(default='slides', max_length=64, validators=[django.core.validators.RegexValidator(code=b'invalid', message=b'Enter a comma-separated list of material types', regex=b'[a-z0-9_-]+(,[a-z0-9_-]+)*')])),
                ('admin_roles', models.CharField(default='chair', max_length=64, validators=[django.core.validators.RegexValidator(code=b'invalid', message=b'Enter a comma-separated list of role slugs', regex=b'[a-z0-9_-]+(,[a-z0-9_-]+)*')])),
                ('history_id', models.AutoField(primary_key=True, serialize=False)),
                ('history_change_reason', models.CharField(max_length=100, null=True)),
                ('history_date', models.DateTimeField()),
                ('history_type', models.CharField(choices=[('+', 'Created'), ('~', 'Changed'), ('-', 'Deleted')], max_length=1)),
                ('agenda_type', models.ForeignKey(blank=True, db_constraint=False, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', to='name.AgendaTypeName')),
                ('history_user', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to=settings.AUTH_USER_MODEL)),
                ('type', ietf.utils.models.ForeignKey(blank=True, db_constraint=False, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', to='name.GroupTypeName')),
            ],
            options={
                'ordering': ('-history_date', '-history_id'),
                'get_latest_by': 'history_date',
                'verbose_name': 'historical group features',
            },
        ),
    ]
