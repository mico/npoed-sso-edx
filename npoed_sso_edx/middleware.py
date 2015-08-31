from social.exceptions import AuthAlreadyAssociated
from social.apps.django_app.middleware import SocialAuthExceptionMiddleware as \
    SocialAuthExceptionMiddlewareBase
from django.shortcuts import render


class SocialAuthExceptionMiddleware(SocialAuthExceptionMiddlewareBase):

    def process_exception(self, request, exception):
        if type(exception) == AuthAlreadyAssociated:
            backend = getattr(request, 'backend', None)
            backend_name = getattr(backend, 'name', 'unknown-backend')
            message = self.get_message(request, exception)
            return render(request, "auth_already_associated.html",
                          {'message': message, 'backend_name': backend_name})

        return super(SocialAuthExceptionMiddleware, self).process_exception(
            request, exception)
