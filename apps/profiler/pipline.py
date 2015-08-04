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

# @partial
# def custom_mail_validation(backend, details, user=None, is_new=False, args, *kwargs):
#     """Email validation pipeline

#     Verify email or send email with validation link.
#     """
#     requires_validation = backend.REQUIRES_EMAIL_VALIDATION or \
#         backend.setting('FORCE_EMAIL_VALIDATION', False)
#     send_validation = (details.get('email') and
#                        (is_new or backend.setting('PASSWORDLESS', False)))

#     if requires_validation and send_validation and backend.name == 'email':
#         data = backend.strategy.request_data()
#         if 'verification_code' in data:
#             backend.strategy.session_pop('email_validation_address')
#             if not backend.strategy.validate_email(
#                     details.get('email'),
#                     data.get('verification_code')
#             ):
#                 raise InvalidEmail(backend)
#             code = backend.strategy.storage.code.get_code(data['verification_code'])
#             # This is very straightforward method
#             # TODO Need to check current user to avoid unnecessary check
#             if code.user_id:
#                 user_from_code = User.objects.filter(id=code.user_id).first()
#                 if user_from_code:
#                     user = user_from_code
#                     logout(backend.strategy.request)
#                     user.backend = 'django.contrib.auth.backends.ModelBackend'
#                     login(backend.strategy.request, user)
#                     return {'user': user}
#         else:
#             if user and user.groups.filter(name='Temporary').exists():
#                 AnonymEmail.objects.get_or_create(
#                     user=user,
#                     email=details.get('email'),
#                     defaults={'date': datetime.now()}
#                 )
#             backend.strategy.send_email_validation(backend, details.get('email'))
#             backend.strategy.session_set(
#                 'email_validation_address', details.get('email')
#             )
#             return backend.strategy.redirect(
#                 backend.strategy.setting('EMAIL_VALIDATION_URL')
#             )
