from social.exceptions import AuthAlreadyAssociated, SocialAuthBaseException
from social.apps.django_app.middleware import SocialAuthExceptionMiddleware as \
    SocialAuthExceptionMiddlewareBase
from django.shortcuts import render
from raven import Client
from django.conf import settings

dsn = getattr(settings, 'RAVEN_CONFIG', {}).get('dsn')
client = None

if dsn:
    client = Client(dsn)


class SocialAuthExceptionMiddleware(SocialAuthExceptionMiddlewareBase):

    def process_exception(self, request, exception):

        if type(exception) == AuthAlreadyAssociated:
            backend = getattr(request, 'backend', None)
            backend_name = getattr(backend, 'name', 'unknown-backend')
            message = self.get_message(request, exception)
            return render(request, "auth_already_associated.html",
                          {'message': message, 'backend_name': backend_name})
        elif isinstance(exception, SocialAuthBaseException):
            if client:
                client.captureMessage('Social Auth Base: {}'.format(
                        self.get_message(request, exception)))
            return render(request, "auth_errors.html", {'message': message})
        else:
            if client:
                client.captureMessage('Another: {}'.format(
                        self.get_message(request, exception)))

        return super(SocialAuthExceptionMiddleware, self).process_exception(
            request, exception)
