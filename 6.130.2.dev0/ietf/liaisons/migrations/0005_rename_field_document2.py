# Copyright The IETF Trust 2019-2020, All Rights Reserved
# -*- coding: utf-8 -*-
# Generated by Django 1.11.20 on 2019-05-21 05:31


from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('doc', '0019_rename_field_document2'),
        ('liaisons', '0004_remove_liaisonstatementattachment_document'),
    ]

    operations = [
        migrations.RenameField(
            model_name='liaisonstatementattachment',
            old_name='document2',
            new_name='document',
        ),
    ]
