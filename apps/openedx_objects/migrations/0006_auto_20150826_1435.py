# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('openedx_objects', '0005_auto_20150821_1247'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='edxcourse',
            options={'verbose_name': 'edxcourse'},
        ),
        migrations.AlterModelOptions(
            name='edxcourseenrollment',
            options={'verbose_name': 'edxcourseenrollment'},
        ),
        migrations.AlterModelOptions(
            name='edxcourserun',
            options={'verbose_name': 'edxcourserun'},
        ),
        migrations.AlterModelOptions(
            name='edxorg',
            options={'verbose_name': 'edxorg'},
        ),
    ]
