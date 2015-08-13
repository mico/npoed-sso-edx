# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('profiler', '0005_auto_20150811_0912'),
    ]

    operations = [
        migrations.RenameField(
            model_name='user',
            old_name='modules',
            new_name='role',
        ),
    ]
