#! /usr/bin/python
# -*- coding: utf-8 -*-

from functools import wraps
from django.template import RequestContext
from django.shortcuts import render_to_response
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth import REDIRECT_FIELD_NAME

User = get_user_model()


def set_auth_cookie(view):
    """
    декоратор для контроля установки и удаленния мультидоменной куки
    логика такая чтоб подсистемы, работающие в общей доменной зоне по этой куке
    могут понять текущий статус авторизованности пользователя
    """
    def wrapper(request, *args, **kwargs):
        response = view(request, *args, **kwargs)
        user = request.user
        is_auth = user.is_authenticated()

        response.set_cookie('authenticated', str(int(is_auth)),
                            domain=settings.AUTH_SESSION_COOKIE_DOMAIN,
                            secure=settings.SESSION_COOKIE_SECURE or None)
        response.set_cookie('authenticated_user',
                            is_auth and user.username or 'Anonymous',
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


def render_to(tpl):
    def decorator(func):
        @wraps(func)
        def wrapper(request, *args, **kwargs):
            out = func(request, *args, **kwargs)
            if isinstance(out, dict):
                out = render_to_response(tpl, out, RequestContext(request))
            return out
        return wrapper
    return decorator
