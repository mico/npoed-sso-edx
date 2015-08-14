#! /usr/bin/python
# -*- coding: utf-8 -*-
"""
    apps.core.views
    ~~~~~~~~~

    :copyright: (c) 2015 by dorosh.
"""

__author__ = 'dorosh'
__date__ = '15.03.2015'

import random
import requests
import json
import urllib
import string

from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponseBadRequest, HttpResponse, JsonResponse
from django.contrib.auth import get_user_model
from django.views.generic.edit import FormView
from django.views.generic import TemplateView
from django.shortcuts import redirect
from django.template.loader import render_to_string
from django.core.urlresolvers import reverse

from provider.oauth2.views import AccessTokenDetailView
from provider.oauth2.models import Client, AccessToken, Grant

from .forms import CreateUserForm
from apps.profiler.forms import RegUserForm, LoginForm
from apps.core.utils import LoginRequiredMixin
from apps.permissions.models import Role
from apps.openedx_objects.models import (
    EdxOrg, EdxCourse, EdxCourseRun, EdxCourseEnrollment
)


User = get_user_model()
url = 'http://rnoep.raccoongang.com/auth/complete/sso_npoed-oauth2/'


class Index(TemplateView):

    template_name = 'index.html'
    success_url = '/'

    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated():
            return redirect(reverse('home'))
        return super(Index, self).get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        form = RegUserForm(request.POST)
        return JsonResponse({
                'status': 'ok' if form.is_valid() else 'error',
                'reg_form': render_to_string('forms/form.html', {'form': form})
                })


class Home(LoginRequiredMixin, FormView):

    template_name = 'home.html'
    form_class = CreateUserForm
    success_url = '/home/'

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)
        if not form.is_valid():
            return super(Home, self).get(request, *args, **kwargs)

        form.save()
        try:
            user = User.objects.get(email=form.cleaned_data['email'])
        except ObjectDoesNotExist:
            return redirect(self.success_url)

        client = Client.objects.filter(redirect_uri=url)
        if client:
            grant = Grant.objects.create(
                user=user,
                client=client[0],
                redirect_uri=url,
                scope=2
            )
            params = urllib.urlencode(
                {
                    'state': ''.join(random.sample(string.ascii_letters, 32)),
                    'code': grant.code
                }
            )
            r = requests.get('%s?%s' % (url, params, ))
        return redirect(self.success_url)


class AccessTokenDetailView(AccessTokenDetailView):

    def get(self, request, *args, **kwargs):
        JSON_CONTENT_TYPE = 'application/json'

        try:
            access_token = AccessToken.objects.get_token(kwargs['token'])
            content = {
                'user_id': access_token.user.id,
                'username': access_token.user.username,
                'email': access_token.user.email,
                'firstname': access_token.user.first_name,
                'lastname': access_token.user.last_name,
                'permissions': [],
                'scope': access_token.get_scope_display(),
                'expires': access_token.expires.isoformat()
            }
            role = access_token.user.role

            for item in role.iterator():
                role_name = '/'.join([item.name, item.modules.name])
                permissions = item.permissions
                orgs = list(permissions.filter(
                    target_type__name=EdxOrg._meta.verbose_name
                ).values('name', 'target_type__name', 'action_type'))
                courses = list(permissions.filter(
                    target_type__name=EdxCourse._meta.verbose_name
                ).values('course_id', 'target_type__name', 'action_type'))
                runs = list(permissions.filter(
                    target_type__name=EdxCourseRun._meta.verbose_name
                ).values(
                    'course__course_id', 'target_type__name', 'action_type'
                ))
                enrollments = list(permissions.filter(
                    target_type__name=EdxCourseEnrollment._meta.verbose_name
                ).values(
                    'course__course_id', 'target_type__name', 'action_type'
                ))
                content['permissions'][role_name] = {
                    EdxOrg._meta.verbose_name: orgs,
                    EdxCourse._meta.verbose_name: courses,
                    EdxCourseRun._meta.verbose_name: runs,
                    EdxCourseEnrollment._meta.verbose_name: enrollments,
                }

            return HttpResponse(json.dumps(content), content_type=JSON_CONTENT_TYPE)
        except ObjectDoesNotExist:
            return HttpResponseBadRequest(json.dumps({'error': 'invalid_token'}),
                                          content_type=JSON_CONTENT_TYPE)
