# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('permissions', '0001_initial'),
    ]

    operations = [
        migrations.DeleteModel(
            name='EdxUserProfile',
        ),
        migrations.RemoveField(
            model_name='edxcourse',
            name='run',
        ),
        migrations.AddField(
            model_name='edxcourserun',
            name='course',
            field=models.ForeignKey(default=None, to='permissions.EdxCourse'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='edxcourseenrollment',
            name='user',
            field=models.ForeignKey(to=settings.AUTH_USER_MODEL, null=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='edxcourserun',
            name='name',
            field=models.CharField(max_length=128),
            preserve_default=True,
        ),
        migrations.AlterUniqueTogether(
            name='edxcourseenrollment',
            unique_together=set([('user', 'course')]),
        ),
        migrations.RemoveField(
            model_name='edxcourseenrollment',
            name='enrollment_id',
        ),
        migrations.AlterUniqueTogether(
            name='edxcourserun',
            unique_together=set([('name', 'course')]),
        ),
    ]
