# Generated by Django 2.0.13 on 2020-07-01 02:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('meeting', '0029_session_tombstone_for'),
    ]

    operations = [
        migrations.AddField(
            model_name='schedule',
            name='notes',
            field=models.TextField(blank=True),
        ),
        migrations.AlterField(
            model_name='schedule',
            name='public',
            field=models.BooleanField(default=True, help_text='Allow others to see this agenda.'),
        ),
        migrations.AlterField(
            model_name='schedule',
            name='visible',
            field=models.BooleanField(default=True, help_text='Show in the list of possible agendas for the meeting.', verbose_name='Show in agenda list'),
        ),
    ]
