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
    date_of_birth = models.DateField(blank=True, null=True)

    # def get_absolute_url(self):
    #     return reverse('user_page', args=(self.id, ))

