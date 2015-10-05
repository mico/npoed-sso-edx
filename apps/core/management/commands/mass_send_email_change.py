#! /usr/bin/python
# -*- coding: utf-8 -*-
from optparse import make_option

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.conf import settings

from apps.profiler.models import send_change_email


User = get_user_model()


class Command(BaseCommand):
    help = 'Send email change mail for all users from the given file'

    option_list = BaseCommand.option_list + (
        make_option('--filename',
                    help='File with bad users'),
    )

    def handle(self, *args, **options):
        if 'filename' not in options:
            self.stdout.write("You have to specify filename")
            return
        else:
            file_user = open(options['filename'], 'r')
            # Expected: user1, user2, ..., user_n
            usernames = file_user.read().replace('\n','').split(',')
            print usernames
            for name in usernames:
                username = name.strip()
                email = None
                try:
                    user = User.objects.get(username=username)
                    email = user.email
                except:
                    self.stdout.write("User with username {} doesn't exist".format(username))
                if email:
                    url_parts = settings.PLP_URL.split('://')
                    sso_url = 'https://sso.{0}'.format(url_parts[1])
                    send_change_email(user, email, sso_url)
                    self.stdout.write("Email sent for user {0} address {1}".format(username, email))
