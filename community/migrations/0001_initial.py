# Copyright The IETF Trust 2018-2020, All Rights Reserved
# -*- coding: utf-8 -*-
# Generated by Django 1.11.10 on 2018-02-20 10:52


from typing import List, Tuple      # pyflakes:ignore

from django.db import migrations, models
import django.db.models.deletion
import ietf.utils.models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]                                   # type: List[Tuple[str]]

    operations = [
        migrations.CreateModel(
            name='CommunityList',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
            ],
        ),
        migrations.CreateModel(
            name='EmailSubscription',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('notify_on', models.CharField(choices=[('all', 'All changes'), ('significant', 'Only significant state changes')], default='all', max_length=30)),
            ],
        ),
        migrations.CreateModel(
            name='SearchRule',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('rule_type', models.CharField(choices=[('group', 'All I-Ds associated with a particular group'), ('area', 'All I-Ds associated with all groups in a particular Area'), ('group_rfc', 'All RFCs associated with a particular group'), ('area_rfc', 'All RFCs associated with all groups in a particular Area'), ('state_iab', 'All I-Ds that are in a particular IAB state'), ('state_iana', 'All I-Ds that are in a particular IANA state'), ('state_iesg', 'All I-Ds that are in a particular IESG state'), ('state_irtf', 'All I-Ds that are in a particular IRTF state'), ('state_ise', 'All I-Ds that are in a particular ISE state'), ('state_rfceditor', 'All I-Ds that are in a particular RFC Editor state'), ('state_ietf', 'All I-Ds that are in a particular Working Group state'), ('author', 'All I-Ds with a particular author'), ('author_rfc', 'All RFCs with a particular author'), ('ad', 'All I-Ds with a particular responsible AD'), ('shepherd', 'All I-Ds with a particular document shepherd'), ('name_contains', 'All I-Ds with particular text/regular expression in the name')], max_length=30)),
                ('text', models.CharField(blank=True, default='', max_length=255, verbose_name='Text/RegExp')),
                ('community_list', ietf.utils.models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='community.CommunityList')),
            ],
        ),
    ]
