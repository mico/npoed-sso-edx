# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('openedx_objects', '0004_edxcourseenrollment_course_run'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='edxcourseenrollment',
            unique_together=set([('user', 'course_run')]),
        ),
        migrations.RemoveField(
            model_name='edxcourseenrollment',
            name='course',
        ),
    ]
