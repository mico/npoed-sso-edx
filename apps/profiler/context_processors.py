#! /usr/bin/python
# -*- coding: utf-8 -*-
"""
    apps.core.views
    ~~~~~~~~~

    :copyright: (c) 2015 by dorosh.
"""

__author__ = 'dorosh'
__date__ = '03.08.2015'

from django.template.loader import render_to_string
from django.conf import settings
from social.backends.google import GooglePlusAuth
from social.backends.utils import load_backends

from apps.profiler.forms import RegUserForm, LoginForm
from registration.forms import RegistrationFormUniqueEmail


def forms(request):
    plp_url = settings.PLP_URL
    # мы хотим, чтобы url PLP в шаблонах был наверняка со слэшом в конце
    if settings.PLP_URL[-1] != '/':
        plp_url = "{}/".format(plp_url)
    return {
        'login_form': render_to_string(
            'forms/form.html', {'form': LoginForm()}
        ),
        'plus_id': getattr(settings, 'SOCIAL_AUTH_GOOGLE_PLUS_KEY', None),
        'plus_scope': ' '.join(GooglePlusAuth.DEFAULT_SCOPE),
        'available_backends': load_backends(settings.AUTHENTICATION_BACKENDS),
        'plp_url': plp_url,
        'social_facebook': getattr(settings, 'SOCIAL_ACCOUNT_FACEBOOK'),
        'social_vk': getattr(settings, 'SOCIAL_ACCOUNT_VK'),
        'social_ok': getattr(settings, 'SOCIAL_ACCOUNT_OK'),
        'social_instagram': getattr(settings, 'SOCIAL_ACCOUNT_INSTAGRAM'),
        'social_twitter': getattr(settings, 'SOCIAL_ACCOUNT_TWITTER'),
    }
