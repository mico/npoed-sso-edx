#! /usr/bin/python
# -*- coding: utf-8 -*-
"""
    apps.core.pipline
    ~~~~~~~~~

    :copyright: (c) 2015 by dorosh.
"""

__author__ = 'dorosh'
__date__ = '26.03.2015'

from .models import User


def save_profile(backend, user, response, *args, **kwargs):
    if backend.name == 'google-oauth2':
        user.first_name = response.get('name', {}).get('givenName', '')
        user.last_name = response.get('name', {}).get('familyName', '')
        user.gender = 1 if response.get('gender') == 'male' else 2
        email = response.get('emails', [{}])[0].get('value', '')
        username = email.split('@')[0]
        if user.username:
            pass
        elif username and not User.objects.filter(username=username).exists():
            user.username = username
        else:
            for item in xrange(500):
                username += str(item)
                if not User.objects.filter(username=username).exists():
                    user.username = username
        user.save()
    elif backend.name == 'facebook':
        print response, '<<<<<<<<<<<<<<<'
        user.gender = 1 if response.get('gender') == 'male' else 2
        user.first_name = response.get('first_name', '')
        user.last_name = response.get('last_name', '')
        user.email = response.get('email', '')
        username = response.get('email', '')
        if user.username:
            pass
        elif username and not User.objects.filter(username=username).exists():
            user.username = username
        else:
            for item in xrange(500):
                username += str(item)
                if not User.objects.filter(username=username).exists():
                    user.username = username
        user.save()
