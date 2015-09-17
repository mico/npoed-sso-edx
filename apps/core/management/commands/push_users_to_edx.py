#! /usr/bin/python
# -*- coding: utf-8 -*-
import random
import requests
import string

from django.contrib.auth import get_user_model
from django.conf import settings
from django.core.management.base import BaseCommand

from provider.oauth2.models import Client, Grant


User = get_user_model()


class Command(BaseCommand):
    help = 'Push all active users to edx'

    def handle(self, *args, **options):
        active_users = User.objects.filter(is_active=True)
        client = Client.objects.filter(redirect_uri=settings.EDX_CRETEUSER_URL)
        if client:
            for user in active_users:
                grant = Grant.objects.create(
                    user=user,
                    client=client[0],
                    redirect_uri=settings.EDX_CRETEUSER_URL,
                    scope=2
                )
                params = {'state': ''.join(random.sample(string.ascii_letters, 32)),
                          'code': grant.code}
                r = requests.get(settings.EDX_CRETEUSER_URL, params, verify=False)
                if r.status_code == 200:
                    self.stdout.write('User: {} created!'.format(user.username))
                elif r.status_code == 401:
                    self.stdout.write('Bad client settings for {}'.format(settings.EDX_CRETEUSER_URL))
                elif r.status_code == 500:
                    self.stdout.write('!!! {} - something bad for this user'.format(user.username))
                elif r.status_code == 404:
                    self.stdout.write('User: {} already exists'.format(user.username))
                else:
                    self.stdout.write('Status code {0} for user {1}'.format(r.status_code, user.username))
        else:
            self.stdout.write('Client for creating users in edx not found')
