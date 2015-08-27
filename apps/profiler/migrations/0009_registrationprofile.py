# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('registration', '__first__'),
        ('profiler', '0008_auto_20150812_1356'),
    ]

    operations = [
        migrations.CreateModel(
            name='RegistrationProfile',
            fields=[
            ],
            options={
                'proxy': True,
            },
            bases=('registration.registrationprofile',),
        ),
    ]
