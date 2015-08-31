# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('profiler', '0012_merge'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='city',
            field=models.CharField(max_length=150, null=True, verbose_name='\u0413\u043e\u0440\u043e\u0434', blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='user',
            name='country',
            field=models.CharField(default=b'ru', max_length=50, verbose_name='\u0421\u0442\u0440\u0430\u043d\u0430'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='user',
            name='date_of_birth',
            field=models.DateField(null=True, verbose_name='\u0414\u0430\u0442\u0430 \u0440\u043e\u0436\u0434\u0435\u043d\u0438\u044f', blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='user',
            name='education',
            field=models.PositiveSmallIntegerField(default=0, verbose_name='\u041e\u0431\u0440\u0430\u0437\u043e\u0432\u0430\u043d\u0438\u0435', choices=[[1, '\u041a\u0430\u043d\u0434\u0438\u0434\u0430\u0442 \u0438\u043b\u0438 \u0434\u043e\u043a\u0442\u043e\u0440 \u043d\u0430\u0443\u043a, PhD'], [2, '\u041c\u0430\u0433\u0438\u0441\u0442\u0440'], [3, '\u0411\u0430\u043a\u0430\u043b\u0430\u0432\u0440'], [4, '\u0421\u043f\u0435\u0446\u0438\u0430\u043b\u0438\u0441\u0442'], [5, '\u041f\u043e\u043b\u043d\u043e\u0435 \u043e\u0431\u0449\u0435\u0435 \u043e\u0431\u0440\u0430\u0437\u043e\u0432\u0430\u043d\u0438\u0435 (10-11 \u043a\u043b\u0430\u0441\u0441\u044b)'], [6, '\u041e\u0441\u043d\u043e\u0432\u043d\u043e\u0435 \u043e\u0431\u0449\u0435\u0435 \u043e\u0431\u0440\u0430\u0437\u043e\u0432\u0430\u043d\u0438\u0435 (5-9 \u043a\u043b\u0430\u0441\u0441\u044b)'], [7, '\u041d\u0430\u0447\u0430\u043b\u044c\u043d\u043e\u0435 \u043e\u0431\u0449\u0435\u0435 \u043e\u0431\u0440\u0430\u0437\u043e\u0432\u0430\u043d\u0438\u0435 (1-4 \u043a\u043b\u0430\u0441\u0441\u044b)'], [8, '\u0411\u0435\u0437 \u043e\u0431\u0440\u0430\u0437\u043e\u0432\u0430\u043d\u0438\u044f'], [9, '\u0414\u0440\u0443\u0433\u043e\u0435'], [0, '\u041d\u0435 \u0443\u043a\u0430\u0437\u0430\u043d\u043e']]),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='user',
            name='gender',
            field=models.PositiveSmallIntegerField(blank=True, null=True, verbose_name='\u041f\u043e\u043b', choices=[[1, '\u043c\u0443\u0436\u0441\u043a\u043e\u0439'], [2, '\u0436\u0435\u043d\u0441\u043a\u0438\u0439']]),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='user',
            name='icon_profile',
            field=models.ImageField(upload_to=b'icon_profile', null=True, verbose_name='\u0424\u043e\u0442\u043e', blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='user',
            name='phone',
            field=models.CharField(max_length=20, null=True, verbose_name='\u0422\u0435\u043b\u0435\u0444\u043e\u043d', blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='user',
            name='post_address',
            field=models.CharField(max_length=255, null=True, verbose_name='\u041f\u043e\u0447\u0442\u043e\u0432\u044b\u0439 \u0430\u0434\u0440\u0435\u0441', blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='user',
            name='second_name',
            field=models.CharField(max_length=50, null=True, verbose_name='\u041e\u0442\u0447\u0435\u0441\u0442\u0432\u043e', blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='user',
            name='time_zone',
            field=models.CharField(default=b'GMT+4', max_length=50, verbose_name='\u0427\u0430\u0441\u043e\u0432\u043e\u0439 \u043f\u043e\u044f\u0441'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='user',
            name='university',
            field=models.CharField(max_length=150, null=True, verbose_name='\u0412\u0443\u0437', blank=True),
            preserve_default=True,
        ),
    ]
