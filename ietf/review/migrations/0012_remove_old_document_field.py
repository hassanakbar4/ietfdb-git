# -*- coding: utf-8 -*-
# Generated by Django 1.11.20 on 2019-05-20 09:53
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('review', '0011_review_document2_fk'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='reviewrequest',
            name='doc',
        ),
        migrations.RemoveField(
            model_name='reviewrequest',
            name='unused_reviewer',
        ),
        migrations.RemoveField(
            model_name='reviewrequest',
            name='unused_review',
        ),
        migrations.RemoveField(
            model_name='reviewrequest',
            name='unused_review2',
        ),
        migrations.RemoveField(
            model_name='reviewrequest',
            name='unused_reviewed_rev',
        ),
        migrations.RemoveField(
            model_name='reviewrequest',
            name='unused_result',
        ),
        migrations.RemoveField(
            model_name='reviewwish',
            name='doc',
        ),
        migrations.RemoveField(
            model_name='reviewassignment',
            name='review',
        ),
    ]
