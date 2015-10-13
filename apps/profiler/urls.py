#! /usr/bin/python
# -*- coding: utf-8 -*-

from django.conf.urls import patterns, url
from django.views.generic import TemplateView

from apps.profiler.views import Profile, UserProfileAPI, UserMassRegistration


urlpatterns = patterns(
    '',
    url(r'^users/me$', UserProfileAPI.as_view(), name='users-me'),
    url(r'^profile/$', Profile.as_view(), name='profile'),
    url(r'^profile_social/$',
        TemplateView.as_view(template_name='profile-social-networks.html'),
        name='profile-social'),
    url(r'^users/mass_registration/$', UserMassRegistration.as_view(), name='users-mass-registration'),
)
