from social.exceptions import AuthAlreadyAssociated, SocialAuthBaseException
from smtplib import SMTPRecipientsRefused

from social.apps.django_app.middleware import SocialAuthExceptionMiddleware as \
    SocialAuthExceptionMiddlewareBase
from django.shortcuts import render
from raven import Client
from django.conf import settings

RAVEN_CONFIG = getattr(settings, 'RAVEN_CONFIG', {})
client = None

if RAVEN_CONFIG:
    client = Client(RAVEN_CONFIG.get('dsn'))


class SocialAuthExceptionMiddleware(SocialAuthExceptionMiddlewareBase):

    def process_exception(self, request, exception):

        message = self.get_message(request, exception)
        backend = getattr(request, 'backend', None)
        backend_name = getattr(backend, 'name', 'unknown-backend')
        if type(exception) == AuthAlreadyAssociated:
            return render(request, "auth_already_associated.html",
                          {'message': message, 'backend_name': backend_name})
        elif isinstance(exception, (SocialAuthBaseException,
                                    SMTPRecipientsRefused, )):
            if client:
                client.captureMessage('Social Auth Base: {}. Backend name: {}'.format(
                        self.get_message(request, exception), backend_name))
            return render(request, "auth_errors.html", {'message': message})
        else:
            if client:
                client.captureMessage('Another: {}'.format(
                        self.get_message(request, exception)))

        return super(SocialAuthExceptionMiddleware, self).process_exception(
            request, exception)
