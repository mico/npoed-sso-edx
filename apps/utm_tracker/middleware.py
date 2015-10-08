# coding: utf8

import urllib
import logging
from django.conf import settings

utm_tags = ['utm_source', 'utm_medium', 'utm_term', 'utm_content', 'utm_campaign']


class UTMTrackingMiddleware(object):
    '''
    Sets cookie if anything from utm_tags is in request.GET
    '''
    def process_response(self, request, response):
        if request and request.GET:
            _ = lambda x: unicode(x).encode('utf-8')
            d = dict([(i, _(request.GET[i])) for i in utm_tags if request.GET.get(i)])
            if d:
                q = urllib.urlencode(d)
                domain = getattr(settings, 'SET_COOKIE_DOMAIN', None)
                response.set_cookie('utm_tags', q, domain=domain)
        return response
