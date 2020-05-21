# Copyright The IETF Trust 2019-2020, All Rights Reserved
# -*- coding: utf-8 -*-
# Generated by Django 1.11.20 on 2019-06-10 03:47


from django.db import migrations
import django.db.models.deletion
import ietf.utils.models


class Migration(migrations.Migration):

    dependencies = [
        ('review', '0013_rename_field_document2'),
    ]

    operations = [
        migrations.AlterField(
            model_name='reviewrequest',
            name='doc',
            field=ietf.utils.models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='reviewrequest_set', to='doc.Document'),
        ),
        migrations.AlterField(
            model_name='reviewwish',
            name='doc',
            field=ietf.utils.models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='doc.Document'),
        ),
    ]
