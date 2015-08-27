#! /usr/bin/python
# -*- coding: utf-8 -*-
"""
    apps.profiler.pipline
    ~~~~~~~~~

    :copyright: (c) 2015 by dorosh.
"""

__author__ = 'dorosh'
__date__ = '04.08.2015'

from django.shortcuts import redirect
from social.pipeline.partial import partial


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
def update_profile(backend, user, response, args, *kwargs):
    if user is None or not response:
        return

    print response
    image_url = None
    profile_url = None

    if backend.name == 'vk-oauth2':
        image_url = response.get('photo_100')
        profile_url = 'https://vk.com/id{}'.format(response.get('uid'))
        user.vkontakte = profile_url
    elif backend.name == 'facebook':
        image_url = 'http://graph.facebook.com/{0}/picture?type=normal'.format(response['id'])
        profile_url = response.get('link')
        print user.icon_profile
        user.icon_profile = profile_url

    if profile_url:
        user.save()

    if image_url and not user.avatar:
        try:
            user.save()
        except Exception as e:
            print e
