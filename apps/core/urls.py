#! /usr/bin/python
# -*- coding: utf-8 -*-
"""
    apps.core.urls
    ~~~~~~~~~

    :copyright: (c) 2015 by dorosh.
"""

__author__ = 'dorosh'
__date__ = '02.08.2015'


from django.conf.urls import patterns, include, url
from apps.core.views import CreateManually, Index, EdxPush


urlpatterns = patterns(
    '', url(r'^$', Index.as_view(), name='index'),
    url(r'^accounts/create_manually/$', CreateManually.as_view(),
        name='create-manually'),
    url(r'^push_to_edx/(?P<pk>\d+)/$', EdxPush.as_view(), name='edx-push')
)
