# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('permissions', '0003_auto_20150810_1017'),
        ('profiler', '0006_auto_20150811_0934'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='user',
            name='role',
        ),
        migrations.AddField(
            model_name='user',
            name='role2',
            field=models.ManyToManyField(to='permissions.Role', null=True, blank=True),
            preserve_default=True,
        ),
    ]
