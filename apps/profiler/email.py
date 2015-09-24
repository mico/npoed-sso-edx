#! /usr/bin/python
# -*- coding: utf-8 -*-
import base64

from django.conf import settings
from django.core.mail import send_mail
from django.core.urlresolvers import reverse

from apps.core.utils import encrypt


def send_validation(strategy, backend, code):
    encoded = base64.b64encode(strategy.request.session.session_key)
    verification_code = encrypt('{0}||{1}'.format(code.code, encoded))

    url = '{0}?verification_code={1}'.format(
        reverse('email_complete', args=(backend.name,)), verification_code
    )
    url = strategy.request.build_absolute_uri(url)
    # Убедимся, что мы правильно ходим в случае https
    url_parts = url.split('://')
    if hasattr(settings, 'URL_PREFIX'):
        url_parts[0] = settings.URL_PREFIX
    text = u'''
    Регистрация на сайте Открытое образование.

    Для активации вашего аккаунта необходимо перейти по ссылке:
    {0}://{1}

    Спасибо!
    '''.format(url_parts[0], url_parts[1])
    send_mail(u'Активация аккаунта Открытое образование', text,
              settings.EMAIL_FROM, [code.email], fail_silently=False)
