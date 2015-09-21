#! /usr/bin/python
# -*- coding: utf-8 -*-

import urllib
import os.path
import os
from uuid import uuid4
from datetime import datetime

from django.contrib.auth.models import AbstractUser
from django.db import models
from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template import RequestContext, TemplateDoesNotExist
from django.template.loader import render_to_string
from django_countries.fields import CountryField

from registration.models import RegistrationProfile as BaseRegistrationProfile

from apps.permissions.models import Role


def path_and_rename(path):
    def wrapper(instance, filename):
        ext = filename.split('.')[-1]
        # set filename as random string
        filename = '{}.{}'.format(uuid4().hex, ext)
        return os.path.join(path, filename[0], filename[1:3], filename)
    return wrapper



class User(AbstractUser):

    sex_choice = [[1, u'мужской'], [2, u'женский']]
    education_choice = [[1, u'Кандидат или доктор наук, PhD'],
                        [2, u'Магистр'],
                        [3, u'Бакалавр'],
                        [4, u'Специалист'],
                        [5, u'Полное общее образование (10-11 классы)'],
                        [6, u'Основное общее образование (5-9 классы)'],
                        [7, u'Начальное общее образование (1-4 классы)'],
                        [8, u'Без образования'],
                        [9, u'Другое'],
                        [0, u'Не указано']]

    # extra userinfo
    second_name = models.CharField(max_length=50, blank=True, null=True, verbose_name=u'Отчество')
    gender = models.PositiveSmallIntegerField(blank=True, null=True, verbose_name=u'Пол',
                                              choices=sex_choice)
    date_of_birth = models.DateField(blank=True, null=True, verbose_name=u'Дата рождения')
    icon_profile = models.ImageField(upload_to=path_and_rename('icon_profile'),
                                     blank=True, null=True, verbose_name=u'Фото')
    # location
    time_zone = models.CharField(max_length=50, default='GMT+4', verbose_name=u'Часовой пояс')
    phone = models.CharField(max_length=20, blank=True, null=True, verbose_name=u'Телефон')
    # country = models.CharField(max_length=50, default='ru', verbose_name=u'Страна')
    country = CountryField(default='RU', verbose_name=u'Страна')
    city = models.CharField(max_length=150, blank=True, null=True, verbose_name=u'Город')
    post_address = models.CharField(max_length=255, blank=True, null=True, verbose_name=u'Почтовый адрес')
    # education
    university = models.CharField(max_length=150, blank=True, null=True, verbose_name=u'Вуз')
    university_group = models.CharField(max_length=150, blank=True, null=True)
    education = models.PositiveSmallIntegerField(
        default=0, choices=education_choice, verbose_name=u'Образование')
    # permissions
    role = models.ManyToManyField(Role, blank=True, null=True)
    # about me field
    about_me = models.TextField(blank=True, null=True, verbose_name=u'О себе')

    def save(self, force_insert=False, force_update=False, using=None,
            update_fields=None):
        try:
            usr = User.objects.get(id=self.id)
            is_active = usr.is_active
        except:
            is_active = False
        super(User, self).save(
            force_insert=force_insert, force_update=force_update, using=using, update_fields=update_fields)
        if self.is_active and not is_active:
            from apps.core.views import push_to_edx
            push_to_edx(self)



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
        prefix = 'http'
        if hasattr(settings, 'URL_PREFIX'):
            prefix = settings.URL_PREFIX
        ctx_dict.update({
            'user': self.user,
            'activation_key': self.activation_key,
            'expiration_days': settings.ACCOUNT_ACTIVATION_DAYS,
            'site': site,
            'redirect_url': urllib.pathname2url(request.GET.get('next', '')),
            'prefix': prefix,
        })

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
