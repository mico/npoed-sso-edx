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

from apps.profiler.views import Profile


urlpatterns = patterns(
    url(r'profile/$', Profile.as_view(), name='profile'),
)
