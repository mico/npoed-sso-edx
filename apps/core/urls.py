#! /usr/bin/python
# -*- coding: utf-8 -*-

from django.conf.urls import patterns, url
from apps.core.views import CreateManually, Index, EdxPush


urlpatterns = patterns(
    '',
    url(r'^$', Index.as_view(), name='index'),
    url(r'^accounts/create_manually/$', CreateManually.as_view(),
        name='create-manually'),
    url(r'^push_to_edx/(?P<pk>\d+)/$', EdxPush.as_view(), name='edx-push')
)
