from django.conf import settings
from django.shortcuts import redirect
from django.contrib.auth.models import User
from django.contrib.auth import REDIRECT_FIELD_NAME


def set_auth_cookie(view):
    def wrapper(request, *args, **kwargs):
        response = view(request, *args, **kwargs)
        is_auth = request.user.is_authenticated()

        response.set_cookie('authenticated', str(int(is_auth)),
                            domain=settings.AUTH_SESSION_COOKIE_DOMAIN,
                            secure=settings.SESSION_COOKIE_SECURE or None)

        return response

    return wrapper


def external_redirect(view):
    def wrapper(request, *args, **kwargs):
        resp = view(request, *args, **kwargs)

        if REDIRECT_FIELD_NAME in request.GET and resp.status_code == 302:
            resp['Location'] = request.GET[REDIRECT_FIELD_NAME]
        return resp

    return wrapper
