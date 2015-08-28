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
from django.contrib.sites.models import Site, RequestSite
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist

from social.backends.oauth import BaseOAuth1, BaseOAuth2
from social.backends.google import GooglePlusAuth
from social.backends.utils import load_backends
from social.apps.django_app.utils import psa

from registration.backends.default.views import (
    ActivationView, RegistrationView as RW
)
from registration import signals
from rest_framework import permissions
from rest_framework.views import APIView
from rest_framework.response import Response

from apps.core.utils import LoginRequiredMixin
from apps.core.decorators import render_to
from apps.profiler.forms import UserForm, LoginForm, RegUserForm
from apps.profiler.models import RegistrationProfile
from apps.permissions.models import Role, Permission
from apps.openedx_objects.models import (
    EdxOrg, EdxCourse, EdxCourseRun, EdxCourseEnrollment
)

User = get_user_model()


class UserProfileAPI(APIView):
    """
    A simple ViewAPI for get user and permissions from open-edx.
    This api call when social-auth through oauth2 from edx asked 
    extra fields user-sso.
    """

    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request):
        user = request.user
        permissions_obj = {}
        content = {
            'user_id': user.id,
            'username': user.username,
            'email': user.email,
            'firstname': user.first_name,
            'lastname': user.last_name,
            'permissions': [],
        }
        for permission in Permission.objects.filter(role__user=user).distinct():
            if permission.target_type is not None:
                obj = permission.get_object()
                if obj is not None:
                    if permission.target_type.name == EdxCourseRun._meta.verbose_name:
                        obj = permission.target_type.model_class().objects.get(
                            pk=permission.target_id
                        )
                        name = obj.course.course_id
                    elif permission.target_type.name == EdxCourse._meta.verbose_name:
                        obj = permission.target_type.model_class().objects.get(
                            pk=permission.target_id
                        )
                        name = obj.course_id
                    else:
                        name = obj.name
                else:
                    if permission.target_id:
                        continue
                    name = '*'
                target_name = permission.target_type.name
            else:
                name = '*'
                target_name = '*'

            key = u'{}/{}'.format(target_name, name)
            obj_dict = permissions_obj.get(key)
            if obj_dict:
                obj_dict['obj_perm'].append(permission.action_type)
                obj_dict['obj_perm'] = list(set(obj_dict['obj_perm']))
            else:
                permissions_obj[key] = {
                    'obj_type': target_name,
                    'obj_id': name,
                    'obj_perm': [permission.action_type],
                }
        content['permissions'] += permissions_obj.values()
        return Response(content)


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

    def register(self, request, **cleaned_data):
        username, email, password = cleaned_data['username'], cleaned_data['email'], cleaned_data['password1']
        if Site._meta.installed:
            site = Site.objects.get_current()
        else:
            site = RequestSite(request)
        new_user = RegistrationProfile.objects.create_inactive_user(
            username, email, password, site,
            send_email=self.SEND_ACTIVATION_EMAIL,
            request=request,
        )
        signals.user_registered.send(sender=self.__class__,
                                     user=new_user,
                                     request=request)
        return new_user


class CustomActivationView(ActivationView):

    def get_success_url(self, request, user):
        next = request.GET.get('next')
        return ('home', (), {}, ) if next is None else next


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
