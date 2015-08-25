#! /usr/bin/python
# -*- coding: utf-8 -*-
"""
    apps.profiler.urls
    ~~~~~~~~~

    :copyright: (c) 2015 by dorosh.
"""

__author__ = 'dorosh'
__date__ = '02.08.2015'

from django.conf.urls import patterns, include, url

from rest_framework.routers import DefaultRouter

from apps.profiler.views import Profile, UserView


urlpatterns = patterns(
    url(r'profile/$', Profile.as_view(), name='profile'),
    url(r'users/me', UserView.as_view(), name='users-me'),
)
