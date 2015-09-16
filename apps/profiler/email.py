#! /usr/bin/python
# -*- coding: utf-8 -*-

from django.conf import settings
from django.core.mail import send_mail
from django.core.urlresolvers import reverse


def send_validation(strategy, backend, code):
    url = '{0}?verification_code={1}'.format(
        reverse('social:complete', args=(backend.name,)),
        code.code
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
