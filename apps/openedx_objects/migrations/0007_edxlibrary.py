# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('openedx_objects', '0006_auto_20150826_1435'),
    ]

    operations = [
        migrations.CreateModel(
            name='EdxLibrary',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('is_published', models.BooleanField(default=True)),
                ('is_archived', models.BooleanField(default=False)),
                ('course_id', models.CharField(unique=True, max_length=255)),
                ('org', models.ForeignKey(to='openedx_objects.EdxOrg')),
            ],
            options={
                'verbose_name': 'edxlibrary',
            },
            bases=(models.Model,),
        ),
    ]
