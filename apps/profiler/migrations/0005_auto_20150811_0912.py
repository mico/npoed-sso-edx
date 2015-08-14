# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('permissions', '0003_auto_20150810_1017'),
        ('profiler', '0004_auto_20150806_1551'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='user',
            options={'verbose_name': 'user', 'verbose_name_plural': 'users'},
        ),
        migrations.AddField(
            model_name='user',
            name='modules',
            field=models.ForeignKey(blank=True, to='permissions.Role', null=True),
            preserve_default=True,
        ),
    ]
