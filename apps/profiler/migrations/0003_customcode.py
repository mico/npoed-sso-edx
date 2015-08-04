# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('default', '0004_auto_20150802_1211'),
        ('profiler', '0002_auto_20150803_1836'),
    ]

    operations = [
        migrations.CreateModel(
            name='CustomCode',
            fields=[
                ('code_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='default.Code')),
                ('user_id', models.IntegerField(null=True)),
            ],
            options={
            },
            bases=('default.code',),
        ),
    ]
