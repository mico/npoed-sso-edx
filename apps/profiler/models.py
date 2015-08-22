#! /usr/bin/python
# -*- coding: utf-8 -*-
"""
    apps.profiler.models
    ~~~~~~~~~

    :copyright: (c) 2015 by dorosh.
"""

__author__ = 'dorosh'
__date__ = '31.08.2015'

import urllib
import os.path

from django.contrib.auth.models import AbstractUser
from django.db import models
from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template import RequestContext, TemplateDoesNotExist
from django.template.loader import render_to_string

from registration.models import RegistrationProfile as BaseRegistrationProfile

from apps.permissions.models import Role


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

    # extra userinfo
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
    # permissions
    role = models.ManyToManyField(Role, blank=True, null=True)


class RegistrationProfile(BaseRegistrationProfile):

     class Meta:
         proxy = True

     def send_activation_email(self, site, request=None):
        ctx_dict = {}
        if request is not None:
            ctx_dict = RequestContext(request, ctx_dict)
        # update ctx_dict after RequestContext is created
        # because template context processors
        # can overwrite some of the values like user
        # if django.contrib.auth.context_processors.auth is used
        ctx_dict.update({
            'user': self.user,
            'activation_key': self.activation_key,
            'expiration_days': settings.ACCOUNT_ACTIVATION_DAYS,
            'site': site,
            'redirect_url': urllib.pathname2url(request.GET.get('next', '')),
        })

        if extra_context:
            ctx_dict.update(extra_context)

        subject = (getattr(settings, 'REGISTRATION_EMAIL_SUBJECT_PREFIX', '') +
                   render_to_string(
                       'registration/activation_email_subject.txt', ctx_dict))

        # Email subject *must not* contain newlines
        subject = ''.join(subject.splitlines())
        from_email = getattr(settings, 'REGISTRATION_DEFAULT_FROM_EMAIL',
                             settings.DEFAULT_FROM_EMAIL)
        message_txt = render_to_string('registration/activation_email.txt',
                                       ctx_dict)

        email_message = EmailMultiAlternatives(subject, message_txt,
                                               from_email, [self.user.email])

        if getattr(settings, 'REGISTRATION_EMAIL_HTML', True):
            try:
                message_html = render_to_string(
                    'registration/activation_email.html', ctx_dict)
            except TemplateDoesNotExist:
                pass
            else:
                email_message.attach_alternative(message_html, 'text/html')

        email_message.send()
