# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('profiler', '0007_auto_20150812_1356'),
    ]

    operations = [
        migrations.RenameField(
            model_name='user',
            old_name='role2',
            new_name='role',
        ),
    ]
