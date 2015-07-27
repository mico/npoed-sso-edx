from django.conf import settings


def set_auth_cookie(view):
    def wrapper(request, *args, **kwargs):
        response = view(request, *args, **kwargs)
        response.set_cookie('authenticated', int(request.user.is_authenticated()).__str__(),
                                                 domain=settings.AUTH_SESSION_COOKIE_DOMAIN,
                                                 secure=settings.SESSION_COOKIE_SECURE or None)
        return response

    return wrapper
