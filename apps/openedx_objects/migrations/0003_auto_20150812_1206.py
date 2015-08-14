# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('openedx_objects', '0002_auto_20150807_1216'),
    ]

    operations = [
        migrations.AlterField(
            model_name='edxcourse',
            name='name',
            field=models.CharField(max_length=128),
            preserve_default=True,
        ),
    ]
