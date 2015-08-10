# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('contenttypes', '0001_initial'),
        ('permissions', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Permission',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('action_type', models.CharField(blank=True, max_length=50, null=True, choices=[(b'*', b'*'), (b'Read', b'Read'), (b'Update', b'Update'), (b'Manage(permissions)', b'Manage(permissions)'), (b'Delete', b'Delete'), (b'DownLoad', b'DownLoad'), (b'Archive', b'Archive'), (b'Create', b'Create'), (b'Publication', b'Publication')])),
                ('target_id', models.PositiveIntegerField(null=True, blank=True)),
                ('target_type', models.ForeignKey(related_name='content_types', blank=True, to='contenttypes.ContentType', null=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.RemoveField(
            model_name='role',
            name='actions',
        ),
        migrations.DeleteModel(
            name='Action',
        ),
        migrations.AddField(
            model_name='role',
            name='permissions',
            field=models.ManyToManyField(to='permissions.Permission', null=True, blank=True),
            preserve_default=True,
        ),
    ]
