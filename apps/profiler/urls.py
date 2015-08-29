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
from django.views.generic import TemplateView

from rest_framework.routers import DefaultRouter

from apps.profiler.views import Profile, UserProfileAPI


urlpatterns = patterns(
    url(r'users/me', UserProfileAPI.as_view(), name='users-me'),
    url(r'profile/$', Profile.as_view(), name='profile'),
    url(r'profile_social',
        TemplateView.as_view(template_name='profile-social-networks.html'),
        name='profile-social'),
)
