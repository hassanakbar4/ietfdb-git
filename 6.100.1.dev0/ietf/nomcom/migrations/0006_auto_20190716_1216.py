# Copyright The IETF Trust 2019, All Rights Reserved
# -*- coding: utf-8 -*-
# Generated by Django 1.11.22 on 2019-07-16 12:16
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('nomcom', '0005_auto_20181008_0602'),
    ]

    operations = [
        migrations.AlterField(
            model_name='feedback',
            name='comments',
            field=models.BinaryField(verbose_name='Comments'),
        ),
    ]
