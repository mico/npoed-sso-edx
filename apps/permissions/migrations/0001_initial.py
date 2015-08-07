# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Action',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('action_type', models.CharField(blank=True, max_length=50, null=True, choices=[(b'*', b'*'), (b'Read', b'Read'), (b'Update', b'Update'), (b'Manage(permissions)', b'Manage(permissions)'), (b'Delete', b'Delete'), (b'DownLoad', b'DownLoad'), (b'Archive', b'Archive'), (b'Create', b'Create'), (b'Publication', b'Publication')])),
                ('target_type', models.CharField(blank=True, max_length=50, null=True, choices=[(b'Org', b'Org'), (b'Course', b'Course'), (b'CourseRun', b'CourseRun'), (b'Profile', b'Profile'), (b'Progress', b'Progress'), (b'Data', b'Data'), (b'VideoFragment', b'VideoFragment')])),
                ('target_id', models.PositiveIntegerField(null=True, blank=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Role',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=50)),
                ('modules', models.CharField(max_length=50, null=True, blank=True)),
                ('actions', models.ManyToManyField(to='permissions.Action', null=True, blank=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]
