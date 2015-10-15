#! /usr/bin/python
# -*- coding: utf-8 -*-
import random
import requests
import string

from django.contrib.auth import get_user_model
from django.conf import settings
from django.core.management.base import BaseCommand

from provider.oauth2.models import Grant, AccessToken, RefreshToken


User = get_user_model()


class Command(BaseCommand):
    help = 'Delete all unusable tokens from db.'

    def handle(self, *args, **options):
        tokens = AccessToken.objects.order_by('user', '-expires').iterator()
        native_item = None
        exclude_list = []
        for item in tokens:
            if native_item != item.user:
                exclude_list.append(item.id)
                native_item = item.user
                
        AccessToken.objects.exclude(id__in=exclude_list).delete()
        RefreshToken.objects.exclude(access_token_id__in=exclude_list).delete()

        self.stdout.write('Clear AccessToken and RefreshToken tables')

        grants = Grant.objects.order_by('user', '-expires').iterator()
        grant_native_item = None
        grant_exclude_list = []
        for item in grants:
            if grant_native_item != item.user:
                grant_exclude_list.append(item.id)
                grant_native_item = item.user
                
        Grant.objects.exclude(id__in=grant_exclude_list).delete()
        self.stdout.write('Clear Grant table')
