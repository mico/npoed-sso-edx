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


def forms(request):
    return {
        'reg_form': render_to_string(
            'forms/form.html', {'form': RegUserForm()}
        ),
        'login_form': render_to_string(
            'forms/form.html', {'form': LoginForm()}
        ),
        'plus_id': getattr(settings, 'SOCIAL_AUTH_GOOGLE_PLUS_KEY', None),
        'plus_scope': ' '.join(GooglePlusAuth.DEFAULT_SCOPE),
        'available_backends': load_backends(settings.AUTHENTICATION_BACKENDS),
    }
