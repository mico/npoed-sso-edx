# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('profiler', '0003_user_tmp_email'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='user',
            options={'permissions': (('change_user_gender', 'Can change the gender of user'),)},
        ),
        migrations.RemoveField(
            model_name='user',
            name='tmp_email',
        ),
    ]
