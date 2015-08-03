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

from .views import (
    MyRegistrationView, Login, UserPage
)


urlpatterns = patterns(
    url(r'^user_page/(?P<pk>\d+)/$', UserPage.as_view(), name='user_page'),

    # url(r'^login_auth/$', Login.as_view(), name='login_auth'),
    url(r'^register/$', MyRegistrationView.as_view(),
        name='registration_register2'),

    url(r'^profile/$', TemplateView.as_view(template_name='profile.html'),
        name='profile'),
)
