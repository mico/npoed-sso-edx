#! /usr/bin/python
# -*- coding: utf-8 -*-
"""
    apps.core.utils
    ~~~~~~~~~

    :copyright: (c) 2015 by dorosh.
"""

__author__ = 'dorosh'
__date__ = '25.03.2015'
__all__ = ['LoginRequiredMixin']

import re
import string
import random

from unidecode import unidecode

from django.contrib.auth.decorators import login_required, user_passes_test
from django.http import Http404

from social.utils import slugify as psa_slugify


url_regex = re.compile(r"""(?i)\b((?:[a-z][\w-]+:(?:/{1,3}|[a-z0-9%])|www\d{0,3}[.]|[a-z0-9.\-]+[.][a-z]{2,4}/)(?:[^\s()<>\[\]]+|\(([^\s()<>\[\]]+|(\([^\s()<>\[\]]+\)))*\))+(?:\(([^\s()<>\[\]]+|(\([^\s()<>\[\]]+\)))*\)|[^\s`!(){};:'".,<>?\[\]]))""")

_DEFAULT_RANDOM_PASSWORD_LENGTH = 12
_PASSWORD_CHARSET = string.letters + string.digits



class LoginRequiredMixin(object):

    @classmethod
    def as_view(cls, **initkwargs):
        view = super(LoginRequiredMixin, cls).as_view(**initkwargs)
        return login_required(view)


def superuser(user):
    if user.is_superuser:
        return user.is_superuser
    raise Http404('Page not found')


class SuperUserRequiredMixin(object):

    @classmethod
    def as_view(cls, **initkwargs):
        view = super(SuperUserRequiredMixin, cls).as_view(**initkwargs)
        return login_required(user_passes_test(superuser)(view))


def slugify(string):
    string = isinstance(string, unicode) and string or string.decode('utf-8')
    return psa_slugify(unidecode(string).decode())


def make_random_password(length=None, choice_fn=random.SystemRandom().choice):
    """Makes a random password.
    When a user creates an account via a social provider, we need to create a
    placeholder password for them to satisfy the ORM's consistency and
    validation requirements. Users don't know (and hence cannot sign in with)
    this password; that's OK because they can always use the reset password
    flow to set it to a known value.
    Args:
        choice_fn: function or method. Takes an iterable and returns a random
            element.
        length: int. Number of chars in the returned value. None to use default.
    Returns:
        String. The resulting password.
    """
    length = length if length is not None else _DEFAULT_RANDOM_PASSWORD_LENGTH
    return ''.join(choice_fn(_PASSWORD_CHARSET) for _ in xrange(length))
