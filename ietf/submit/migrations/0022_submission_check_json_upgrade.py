# -*- coding: utf-8 -*-
# Generated by Django 1.10.8 on 2017-10-27 06:34
from __future__ import unicode_literals

from django.db import migrations

# convert the SubmissionCheck.items to consistently be a dict, with the
# following content:
#    {
#      'checker': <string>;
#      'message': <string>;
#      'items': <list>;     # error or warning items
#      'draft': <draftname>;
#      'modules': { <extracted module info> },
#    }


def forwards(apps, schema_editor):
    SubmissionCheck = apps.get_model('submit', 'SubmissionCheck')
    for check in SubmissionCheck.objects.all().order_by('id'):
        # deal with these cases:
        #   * empty dictionary
        #   * empty list
        #   * dictionary with idnits info
        #   * list with yang errors and warnings
        items = []
        if   check.items == {} or check.items == '{}':
            pass
        elif check.items == []:
            pass
        elif type(check.items) == dict:
            if 'checker' in check.items:
                continue
        elif type(check.items) == list:
            items = check.items
        else:
            raise ValueError("Unexpected check.items value: %s: %s" % (type(check.items), check.items))
        check.items = {
            'checker':  check.checker,
            'draft':    check.submission.name,
            'rev':      check.submission.rev,
            'items':    items,
            'code':  {},
        }
        check.save()

def backwards(apps, schema_editor):
    pass

class Migration(migrations.Migration):

    dependencies = [
        ('meeting', '0058_set_new_field_meeting_days_values'),
        ('submit', '0021_submissioncheck_time_default'),
    ]

    operations = [
        migrations.RunPython(forwards, backwards),
    ]
