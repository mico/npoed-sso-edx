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

from unidecode import unidecode

from django.contrib.auth.decorators import login_required

from social.utils import slugify as psa_slugify


url_regex = re.compile(r"""(?i)\b((?:[a-z][\w-]+:(?:/{1,3}|[a-z0-9%])|www\d{0,3}[.]|[a-z0-9.\-]+[.][a-z]{2,4}/)(?:[^\s()<>\[\]]+|\(([^\s()<>\[\]]+|(\([^\s()<>\[\]]+\)))*\))+(?:\(([^\s()<>\[\]]+|(\([^\s()<>\[\]]+\)))*\)|[^\s`!(){};:'".,<>?\[\]]))""")

class LoginRequiredMixin(object):

    @classmethod
    def as_view(cls, **initkwargs):
        view = super(LoginRequiredMixin, cls).as_view(**initkwargs)
        return login_required(view)


def slugify(string):
    string = isinstance(string, unicode) and string or string.decode('utf-8')
    return psa_slugify(unidecode(string).decode())
