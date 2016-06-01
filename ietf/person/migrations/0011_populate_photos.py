# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import os

from hashids import Hashids

from django.db import migrations
from django.conf import settings
from django.utils.text import slugify

def photo_name(person,thumb=False):
    hasher = Hashids(salt='Person photo name salt',min_length=5)
    return '%s-%s%s' % ( slugify(person.ascii), hasher.encode(person.id), '-th' if thumb else '' )

def forward(apps,schema_editor):
    Person = apps.get_model('person','Person')
    images_dir = os.path.join(settings.PHOTOS_DIR,settings.PHOTO_URL_PREFIX)
    image_filenames = []
    for (dirpath, dirnames, filenames) in os.walk(images_dir):
        image_filenames.extend(filenames)
        break # Only interested in the files in the top directory
    image_basenames = [os.path.splitext(name)[0] for name in image_filenames]
    for person in Person.objects.all():
        dirty = False
        if photo_name(person,thumb=False) in image_basenames:
            person.photo = image_filenames[image_basenames.index(photo_name(person,thumb=False))]
            dirty = True
        if photo_name(person,thumb=True) in image_basenames:
            person.photo_thumb = image_filenames[image_basenames.index(photo_name(person,thumb=True))]
            dirty = True
        if dirty:
            person.save()

def reverse(apps, schema_editor):
    pass

class Migration(migrations.Migration):

    dependencies = [
        ('person', '0010_add_photo_fields'),
    ]

    operations = [
        migrations.RunPython(forward,reverse)
    ]
