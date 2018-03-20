# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations


def backfill_old_meetings(apps, schema_editor):
        Meeting          = apps.get_model('meeting', 'Meeting')

        for number, attendees in [
                ( 71,1174 ),
                ( 70,1128 ),
                ( 69,1175 ),
                ( 68,1193 ),
                ( 67,1245 ),
                ( 66,1257 ),
                ( 65,1264 ),
                ( 64,1240 ),
                ( 63,1450 ),
                ( 62,1133 ),
                ( 61,1311 ),
                ( 60,1460 ),
                ( 59,1390 ),
                ( 58,1233 ),
                ( 57,1304 ),
                ( 56,1679 ),
                ( 55,1570 ),
                ( 54,1885 ),
                ( 53,1656 ),
                ( 52,1691 ),
                ( 51,2226 ),
                ( 50,1822 ),
                ( 49,2810 ),
                ( 48,2344 ),
                ( 47,1431 ),
                ( 46,2379 ),
                ( 45,1710 ),
                ( 44,1705 ),
                ( 43,2124 ),
                ( 42,2106 ),
                ( 41,1775 ),
                ( 40,1897 ),
                ( 39,1308 ),
                ( 38,1321 ),
                ( 37,1993 ),
                ( 36,1283 ),
                ( 35,1038 ),
                ( 34,1007 ),
                ( 33,617 ),
                ( 32,983 ),
                ( 31,1079 ),
                ( 30,710 ),
                ( 29,785 ),
                ( 28,636 ),
                ( 27,493 ),
                ( 26,638 ),
                ( 25,633 ),
                ( 24,677 ),
                ( 23,530 ),
                ( 22,372 ),
                ( 21,387 ),
                ( 20,348 ),
                ( 19,292 ),
                ( 18,293 ),
                ( 17,244 ),
                ( 16,196 ),
                ( 15,138 ),
                ( 14,217 ),
                ( 13,114 ),
                ( 12,120 ),
                ( 11,114 ),
                ( 10,112 ),
                ( 9,82 ),
                ( 8,56 ),
                ( 7,101 ),
                ( 6,88 ),
                ( 5,35 ),
                ( 4,35 ),
                ( 3,18 ),
                ( 2,21 ),
                ( 1,21 ),
        ]:
                meeting = Meeting.objects.filter(type='ietf',
                                                 number=number).first();
                meeting.attendees = attendees
                meeting.save()
        
class Migration(migrations.Migration):

    dependencies = [
        ('meeting', '0005_backfill_old_meetings'),
    ]

    operations = [
        migrations.RunPython(backfill_old_meetings)
    ]
            
