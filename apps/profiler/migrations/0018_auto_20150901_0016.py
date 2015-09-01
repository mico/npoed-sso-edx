# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django_countries.fields


class Migration(migrations.Migration):

    dependencies = [
        ('profiler', '0017_merge'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='about_me',
            field=models.TextField(null=True, verbose_name='\u041e \u0441\u0435\u0431\u0435', blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='user',
            name='country',
            field=django_countries.fields.CountryField(default=b'RU', max_length=2, verbose_name='\u0421\u0442\u0440\u0430\u043d\u0430'),
            preserve_default=True,
        ),
    ]
