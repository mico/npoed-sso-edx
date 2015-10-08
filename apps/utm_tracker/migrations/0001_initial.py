# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.db.models.deletion
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='UTMUserTags',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('utm_source', models.CharField(max_length=255, null=True, blank=True)),
                ('utm_medium', models.CharField(max_length=255, null=True, blank=True)),
                ('utm_term', models.CharField(max_length=255, null=True, blank=True)),
                ('utm_content', models.CharField(max_length=255, null=True, blank=True)),
                ('utm_campaign', models.CharField(max_length=255, null=True, blank=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL, null=True)),
            ],
            options={
                'verbose_name': 'Utm-\u043c\u0435\u0442\u043a\u0430 \u043f\u043e\u043b\u044c\u0437\u043e\u0432\u0430\u0442\u0435\u043b\u044f',
                'verbose_name_plural': 'Utm-\u043c\u0435\u0442\u043a\u0438 \u043f\u043e\u043b\u044c\u0437\u043e\u0432\u0430\u0442\u0435\u043b\u0435\u0439',
            },
            bases=(models.Model,),
        ),
    ]
