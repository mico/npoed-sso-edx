#! /usr/bin/python
# -*- coding: utf-8 -*-
"""
    apps.core.views
    ~~~~~~~~~

    :copyright: (c) 2015 by dorosh.
"""

__author__ = 'dorosh'
__date__ = '15.03.2015'

import json

from django.shortcuts import redirect
from django.conf import settings
from django.views.generic.edit import FormView, UpdateView
from django.views.generic import View, ListView, TemplateView, DetailView
from django.http import HttpResponse, HttpResponseBadRequest, JsonResponse
from django.contrib.auth import (
    authenticate, login, get_user_model, logout as auth_logout
)
from django.template.loader import render_to_string
from django.core.mail import send_mail
from django.core.urlresolvers import reverse
from django.contrib.sites.models import Site
from django.contrib.auth.decorators import login_required

from social.backends.oauth import BaseOAuth1, BaseOAuth2
from social.backends.google import GooglePlusAuth
from social.backends.utils import load_backends
from social.apps.django_app.utils import psa

from registration.backends.default.views import (
    ActivationView, RegistrationView as RW
)
from registration.models import RegistrationProfile

from apps.core.utils import LoginRequiredMixin
from apps.core.decorators import render_to
from apps.profiler.forms import UserForm, LoginForm, RegUserForm

User = get_user_model()


def context(**extra):
    return dict({
        'plus_id': getattr(settings, 'SOCIAL_AUTH_GOOGLE_PLUS_KEY', None),
        'plus_scope': ' '.join(GooglePlusAuth.DEFAULT_SCOPE),
        'available_backends': load_backends(settings.AUTHENTICATION_BACKENDS)
    }, **extra)


class Login(FormView):

    form_class = LoginForm

    def post(self, request, *args, **kwargs):
        form = self.form_class(data=request.POST)
        return JsonResponse({
                'status': 'ok' if form.is_valid() else 'error',
                'form': render_to_string('forms/login_form.html', {'form': form})
                })


class Profile(LoginRequiredMixin, UpdateView):

    template_name = 'profile.html'
    form_class = UserForm
    success_url = '/profile/'
    model = User

    def get_object(self, queryset=None):
        return self.request.user


class RegistrationView(RW):

    form_class = RegUserForm

    def get_success_url(self, request=None, user=None):
        # We need to be able to use the request and the new user when
        # constructing success_url.
        return ('home', (), {})


class CustomActivationView(ActivationView):

    def get_success_url(self, request, user):
        return reverse('index')


@login_required
@render_to('index.html')
def done(request):
    """Login complete view, displays user data"""
    return context()


@render_to('index.html')
def validation_sent(request):
    return context(
        validation_sent=True,
        email=request.session.get('email_validation_address')
    )


@render_to('index.html')
def require_email(request):
    backend = request.session['partial_pipeline']['backend']
    return context(email_required=True, backend=backend)


@psa('social:complete')
def ajax_auth(request, backend):
    if isinstance(request.backend, BaseOAuth1):
        token = {
            'oauth_token': request.REQUEST.get('access_token'),
            'oauth_token_secret': request.REQUEST.get('access_token_secret'),
        }
    elif isinstance(request.backend, BaseOAuth2):
        token = request.REQUEST.get('access_token')
    else:
        raise HttpResponseBadRequest('Wrong backend type')
    user = request.backend.do_auth(token, ajax=True)
    login(request, user)
    data = {'id': user.id, 'username': user.username}
    return HttpResponse(json.dumps(data), mimetype='application/json')
