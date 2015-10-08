# coding: utf8

import urlparse
import logging
from urllib import unquote
from django.db import models
from django.conf import settings
from django.dispatch import receiver
from registration.signals import user_registered


class UTMUserTags(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, on_delete=models.SET_NULL)
    utm_source = models.CharField(max_length=255, blank=True, null=True)
    utm_medium = models.CharField(max_length=255, blank=True, null=True)
    utm_term = models.CharField(max_length=255, blank=True, null=True)
    utm_content = models.CharField(max_length=255, blank=True, null=True)
    utm_campaign = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        verbose_name = u'Utm-метка пользователя'
        verbose_name_plural = u'Utm-метки пользователей'


@receiver(user_registered)
def process_registered_user(sender, user, request, **kwargs):
    '''
    add new UTMUserTags object if 'utm_tags' in cookies and
    user not in UTMUserTags
    '''
    process_new_utm_creation(request, user)


def process_new_utm_creation(request, user):
    if 'utm_tags' in request.COOKIES:
        try:
            if not UTMUserTags.objects.filter(user=user).exists():
                cookie = request.COOKIES['utm_tags']
                q = dict((k, unquote(v[0])[:255]) for k, v in urlparse.parse_qs(cookie).items())
                q['user'] = user
                UTMUserTags.objects.create(**q)
        except Exception as e:
            logging.error('Error while trying to save %s for %s: %s' %
                          (request.COOKIES.get('utm_tags'), user, e))
