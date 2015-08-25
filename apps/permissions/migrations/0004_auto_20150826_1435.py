# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('permissions', '0003_auto_20150810_1017'),
    ]

    operations = [
        migrations.AlterField(
            model_name='permission',
            name='action_type',
            field=models.CharField(blank=True, max_length=50, null=True, choices=[(b'*', b'*'), (b'Read', b'Read'), (b'Update', b'Update'), (b'Manage(permissions)', b'Manage(permissions)'), (b'Delete', b'Delete'), (b'DownLoad', b'DownLoad'), (b'Archive', b'Archive'), (b'Create', b'Create'), (b'Publication', b'Publication'), (b'Enroll', b'Enroll')]),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='role',
            name='name',
            field=models.CharField(unique=True, max_length=50),
            preserve_default=True,
        ),
    ]
