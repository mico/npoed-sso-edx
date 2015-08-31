# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django_countries.fields


class Migration(migrations.Migration):

    dependencies = [
        ('profiler', '0014_verbose_name_for_about_me_field'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='country',
            field=django_countries.fields.CountryField(default=b'RU', max_length=2, verbose_name='\u0421\u0442\u0440\u0430\u043d\u0430'),
            preserve_default=True,
        ),
    ]
