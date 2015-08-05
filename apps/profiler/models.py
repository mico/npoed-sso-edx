#! /usr/bin/python
# -*- coding: utf-8 -*-
"""
    apps.profiler.models
    ~~~~~~~~~

    :copyright: (c) 2015 by dorosh.
"""

__author__ = 'dorosh'
__date__ = '31.08.2015'

import os.path

from django.contrib.auth.models import AbstractUser
from django.db import models
from django.conf import settings


class User(AbstractUser):
    '''
    Here is your User class which is fully customizable and
    based off of the AbstractUser from auth.models
    '''

    sex_choice = [[1, 'male'], [2, 'female']]
    education_choice = [[1, u'Кандидат или доктор наук, PhD'],
                        [2, u'Магистр'],
                        [3, u'Бакалавр'],
                        [4, u'Специалист'],
                        [5, u'Полное общее образование'],
                        [6, u'Основное общее образование'],
                        [7, u'Начальное общее образование'],
                        [8, u'Без образования'],
                        [9, u'Другое'],
                        [0, u'Не указан']]

    # email = models.CharField(max_length=50, unique=True)
    second_name = models.CharField(max_length=50, blank=True, null=True)
    gender = models.PositiveSmallIntegerField(blank=True, null=True,
                                              choices=sex_choice)
    date_of_birth = models.DateField(blank=True, null=True)
    icon_profile = models.ImageField(upload_to='icon_profile',
                                     blank=True, null=True)
    # location
    time_zone = models.CharField(max_length=50, default='GMT+4')
    phone = models.CharField(max_length=20, blank=True, null=True)
    country = models.CharField(max_length=50, default='ru')
    city = models.CharField(max_length=150, blank=True, null=True)
    post_address = models.CharField(max_length=255, blank=True, null=True)
    # education
    university = models.CharField(max_length=150, blank=True, null=True)
    university_group = models.CharField(max_length=150, blank=True, null=True)
    education = models.PositiveSmallIntegerField(
        default=0, choices=education_choice)
    # tmp
    tmp_email = models.EmailField(max_length=150, blank=True, null=True)
    
    # def get_absolute_url(self):
    #     return reverse('user_page', args=(self.id, ))
