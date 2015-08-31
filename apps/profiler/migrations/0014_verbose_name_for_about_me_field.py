# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('profiler', '0013_auto_20150831_1140'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='about_me',
            field=models.TextField(null=True, verbose_name='\u041e \u0441\u0435\u0431\u0435', blank=True),
            preserve_default=True,
        ),
    ]
