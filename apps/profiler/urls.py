#! /usr/bin/python
# -*- coding: utf-8 -*-

from django.conf.urls import patterns, url
from django.views.generic import TemplateView

from apps.profiler.views import Profile, UserProfileAPI, EmailValidation


urlpatterns = patterns(
    '',
    url(r'^users/me$', UserProfileAPI.as_view(), name='users-me'),
    url(r'^profile/$', Profile.as_view(), name='profile'),
    url(r'^validation_email/$', EmailValidation.as_view(),
        name='validation_email'),
    url(r'^profile_social/$',
        TemplateView.as_view(template_name='profile-social-networks.html'),
        name='profile-social'),
)
