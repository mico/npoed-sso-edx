# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='EdxCourse',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('is_published', models.BooleanField(default=True)),
                ('is_archived', models.BooleanField(default=False)),
                ('name', models.CharField(unique=True, max_length=128)),
                ('course_id', models.CharField(unique=True, max_length=255)),
                ('start', models.DateTimeField()),
                ('end', models.DateTimeField(null=True)),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='EdxCourseEnrollment',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('is_published', models.BooleanField(default=True)),
                ('is_archived', models.BooleanField(default=False)),
                ('name', models.CharField(max_length=128, blank=True)),
                ('enrollment_id', models.IntegerField(unique=True)),
                ('mode', models.CharField(default=b'honor', max_length=100)),
                ('is_active', models.BooleanField(default=True)),
                ('course', models.ForeignKey(to='openedx_objects.EdxCourse')),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='EdxCourseRun',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('is_published', models.BooleanField(default=True)),
                ('is_archived', models.BooleanField(default=False)),
                ('name', models.CharField(unique=True, max_length=128)),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='EdxOrg',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('is_published', models.BooleanField(default=True)),
                ('is_archived', models.BooleanField(default=False)),
                ('name', models.CharField(unique=True, max_length=128)),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='EdxUserProfile',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('is_published', models.BooleanField(default=True)),
                ('is_archived', models.BooleanField(default=False)),
                ('username', models.CharField(unique=True, max_length=30)),
                ('name', models.CharField(max_length=128, blank=True)),
                ('email', models.EmailField(max_length=75, blank=True)),
                ('is_active', models.BooleanField(default=True)),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='edxcourse',
            name='org',
            field=models.ForeignKey(to='openedx_objects.EdxOrg'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='edxcourse',
            name='run',
            field=models.ForeignKey(to='openedx_objects.EdxCourseRun'),
            preserve_default=True,
        ),
    ]
