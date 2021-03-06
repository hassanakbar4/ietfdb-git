# Generated by Django 2.2.16 on 2020-10-28 09:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('person', '0016_auto_20200807_0750'),
    ]

    operations = [
        migrations.AlterField(
            model_name='historicalperson',
            name='plain',
            field=models.CharField(blank=True, default='', help_text="Use this if you have a Spanish double surname.  Don't use this for nicknames, and don't use it unless you've actually observed that the datatracker shows your name incorrectly.", max_length=64, verbose_name='Plain Name correction (Unicode)'),
        ),
        migrations.AlterField(
            model_name='person',
            name='plain',
            field=models.CharField(blank=True, default='', help_text="Use this if you have a Spanish double surname.  Don't use this for nicknames, and don't use it unless you've actually observed that the datatracker shows your name incorrectly.", max_length=64, verbose_name='Plain Name correction (Unicode)'),
        ),
    ]
