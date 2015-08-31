#! /usr/bin/python
# -*- coding: utf-8 -*-
"""
    apps.profiler.pipline
    ~~~~~~~~~

    :copyright: (c) 2015 by dorosh.
"""

__author__ = 'dorosh'
__date__ = '04.08.2015'

from datetime import datetime

from django.core.files.storage import default_storage
from django.shortcuts import redirect
from django.core.files.base import ContentFile

from social.pipeline.partial import partial

from apps.core.utils import make_random_password


@partial
def require_email(strategy, details, user=None, is_new=False, *args, **kwargs):
    if kwargs.get('ajax') or user and user.email:
        return
    elif is_new and not details.get('email'):
        email = strategy.request_data().get('email')
        if email:
            details['email'] = email
            details['validation'] = True
        else:
            return redirect('require_email')


@partial
def mail_validation(backend, details, is_new=False, *args, **kwargs):
    requires_validation = backend.REQUIRES_EMAIL_VALIDATION or \
                          backend.setting('FORCE_EMAIL_VALIDATION', False)
    send_validation = details.get('email') and \
                      (is_new or backend.setting('PASSWORDLESS', False)) and details.get('validation')
    if requires_validation and send_validation:
        data = backend.strategy.request_data()
        if 'verification_code' in data:
            backend.strategy.session_pop('email_validation_address')
            if not backend.strategy.validate_email(details['email'],
                                           data['verification_code']):
                raise InvalidEmail(backend)
        else:
            backend.strategy.send_email_validation(backend, details['email'])
            backend.strategy.session_set('email_validation_address',
                                         details['email'])
            return backend.strategy.redirect(
                backend.strategy.setting('EMAIL_VALIDATION_URL')
            )


@partial
def update_profile(backend, user, response, *args, **kwargs):
    if user is None or not response:
        return

    gender_dict = {'male': 1, 'female': 2}
    change_data = False
    image_url = None

    if backend.name == 'vk-oauth2':
        image_url = response.get('photo_100')
        gender = response.get('sex')
        if not user.gender and gender:
            change_data = True
            # in vk male has id 2, female has id 1
            user.gender = {2: 1, 1: 2}.get(gender)

        bdate = response.get('bdate')
        if not user.date_of_birth and bdate:
            bdate = datetime.strptime(bdate, "%d.%m.%Y").date()
            user.date_of_birth = bdate
            change_data = True

    elif backend.name == 'facebook':
        image_url = 'http://graph.facebook.com/{0}/picture?type=normal'.format(response['id'])
        gender = response.get('gender')
        if not user.gender and gender:
            change_data = True
            user.gender = gender_dict.get(gender)

    elif backend.name == 'twitter':
        image_url = response.get('profile_image_url')
        country = response.get('country')
        if not user.country and country:
            change_data = True
            user.country = country

    elif backend.name == 'google-oauth2':
        
        gender = response.get('gender')
        if not user.gender and gender:
            change_data = True
            user.gender = gender_dict.get(gender)

    elif backend.name == 'mailru-oauth2':

        gender = response.get('sex')
        if not user.gender and gender:
            change_data = True
            # in mailru male has id 0, female has id 1
            user.gender = {0: 1, 1: 2}.get(gender)

        birthday = response.get('birthday')
        if not user.date_of_birth and birthday:
            try:
                birthday = datetime.strptime(birthday, "%d.%m.%Y").date()
            except ValueError:
                pass
            else:
                user.date_of_birth = birthday
                change_data = True

    if change_data:
        user.save()

    if not user.has_usable_password():
        user.set_password(make_random_password())
        user.save()

    if image_url and not user.icon_profile:
        try:
            image_content = urlopen(image_url)
            image_name = default_storage.get_available_name(
                user.icon_profile.field.upload_to + '/' + str(user.id) + '.' + image_content.headers.subtype)
            user.icon_profile.save(image_name, ContentFile(image_content.read()))
            user.save()
        except Exception:
            pass
