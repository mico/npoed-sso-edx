# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('openedx_objects', '0003_auto_20150812_1206'),
    ]

    operations = [
        migrations.AddField(
            model_name='edxcourseenrollment',
            name='course_run',
            field=models.ForeignKey(default=None, to='openedx_objects.EdxCourseRun'),
            preserve_default=False,
        ),
    ]
