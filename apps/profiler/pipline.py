#! /usr/bin/python
# -*- coding: utf-8 -*-
"""
    apps.profiler.pipline
    ~~~~~~~~~

    :copyright: (c) 2015 by dorosh.
"""

__author__ = 'dorosh'
__date__ = '04.08.2015'

from social.exceptions import InvalidEmail
from social.pipeline.partial import partial
from django.core.urlresolvers import reverse
from django.conf import settings
from django.shortcuts import redirect
from django.core.mail import send_mail


def redirect_if_no_email(backend, response, social, *args, **kwargs):
    if not kwargs['details'].get('email'):
        return redirect(reverse('social:complete', args=('email',)))


def send_validation(strategy, backend, code):
    """
    Send email validation link.
    """
    # TODO add email validating regex [^@]+@[^@]+\.[^@]+
    url = (reverse('social:complete', args=(backend.name,)) +
           '?verification_code=' + code.code)
    url = strategy.request.build_absolute_uri(url)
    print strategy, backend, code
    send_mail(
        'Validate your account',
        'Validate your account {0}'.format(url),
        settings.FROM_EMAIL,
        [code.email],
        fail_silently=False
    )

from django.template import RequestContext
from django.shortcuts import render_to_response
from django.contrib.auth import login, logout
# from django.core.mail import send_mail
from django.conf import settings
from django.db import IntegrityError
from django.contrib.auth.models import User
import time
from datetime import datetime

from social.pipeline.partial import partial
from social.exceptions import (InvalidEmail,
                               AuthException,
                               AuthAlreadyAssociated)
from social.backends.utils import load_backends
from social.apps.django_app.default.models import UserSocialAuth


@partial
def validated_user_details(strategy, backend, details, user=None, *args, **kwargs):
    """Merge actions
    Make different merge actions based on user type.
    """
    social = kwargs.get('social')
    email = details.get('email')
    if user and user.groups.filter(name='Temporary').exists():
        if social:
            logout(strategy.request)
            social.user.backend = 'django.contrib.auth.backends.ModelBackend'
            login(strategy.request, social.user)
            union_merge(user, social.user)
            user.delete()
            return {'user': social.user}
        else:
            new_user = None
            if email:
                users = list(backend.strategy.storage.user.get_users_by_email(email))
                if len(users) == 0:
                    pass
                elif len(users) > 1:
                    raise AuthException(
                        backend,
                        'The given email address is associated with another account'
                    )
                else:
                    new_user = users[0]
            if not new_user:
                try:
                    user.username = details.get('username')
                    user.first_name = ''
                    user.save()
                except IntegrityError:
                    _id = int(time.mktime(datetime.now().timetuple()))
                    user.username = details.get('username') + str(_id)
                    user.save()
            else:
                logout(strategy.request)
                new_user.backend = 'django.contrib.auth.backends.ModelBackend'
                login(strategy.request, new_user)
                union_merge(user, new_user)
                user.delete()
                return {'user': new_user}
    elif user and social and social.user != user:
        confirm = strategy.request.POST.get('confirm')
        if confirm and confirm == 'no':
            raise AuthException(
                backend,
                'You interrupted merge process.'
            )
        elif (not user.get_full_name() == social.user.get_full_name() and
              not strategy.request.POST.get('confirm') and
              not user.email == social.user.email):

            return redirect(reverse('social:complete', args=('email',)))
            # return render_to_response('ct/person.html', {
            #     'available_backends': load_backends(settings.AUTHENTICATION_BACKENDS),
            #     'request': strategy.request,
            #     'next': strategy.request.POST.get('next') or '',
            #     'target_name': social.user.get_full_name(),
            #     'own_name': user.get_full_name(),
            #     'person': user,
            #     'merge_confirm': True
            # }, RequestContext(strategy.request))

        elif (user.get_full_name() == social.user.get_full_name() or
              confirm and confirm == 'yes' or user.email == social.user.email):
            union_merge(social.user, user)
            social_merge(social.user, user)
            social.user.delete()
            social.user = user
            return {'user': user,
                    'social': social}
