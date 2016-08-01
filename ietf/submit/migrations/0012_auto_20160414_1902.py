# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):
    def add_draft_submission_state_name(apps, schema_editor):
        # We can't import the model directly as it may be a newer
        # version than this migration expects. We use the historical version.
        DraftSubmissionStateName = apps.get_model("name", "DraftSubmissionStateName")
        DraftSubmissionStateName.objects.create(slug="manual-awaiting-draft",
                                                name="Manual Post Awaiting Draft",
                                                desc="",
                                                used=True,
                                                order=8)


    dependencies = [
        ('submit', '0011_submissionemail'),
    ]

    operations = [
        migrations.RunPython(add_draft_submission_state_name),
    ]
