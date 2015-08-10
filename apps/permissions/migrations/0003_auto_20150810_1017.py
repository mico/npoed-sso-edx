# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('permissions', '0002_auto_20150810_1012'),
    ]

    operations = [
        migrations.AlterField(
            model_name='role',
            name='modules',
            field=models.ForeignKey(blank=True, to='provider.Client', null=True),
            preserve_default=True,
        ),
    ]
