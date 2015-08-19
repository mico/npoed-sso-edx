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
from djaango.conf import settings

from provider.oauth2.views import AccessTokenDetailView as AccessTokenDetailView_origin
from provider.oauth2.models import Client, AccessToken, Grant

from .forms import CreateUserForm
from apps.profiler.forms import RegUserForm, LoginForm
from apps.core.utils import LoginRequiredMixin
from apps.permissions.models import Role, Permission
from apps.openedx_objects.models import (
    EdxOrg, EdxCourse, EdxCourseRun, EdxCourseEnrollment
)


User = get_user_model()


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
                redirect_uri=settings.EDX_CRETEUSER_URL,
                scope=2
            )
            params = urllib.urlencode(
                {
                    'state': ''.join(random.sample(string.ascii_letters, 32)),
                    'code': grant.code
                }
            )
            r = requests.get('%s?%s' % (settings.EDX_CRETEUSER_URL, params, ))
        return redirect(self.success_url)


class AccessTokenDetailView(AccessTokenDetailView_origin):

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

            roles_ids = access_token.user.role.values_list('id', flat=True)
            permissions_obj = {}
            for permission in Permission.objects.filter(role__in=list(roles_ids)).distinct():
                try:
                    if permission.target_type is not None:
                        obj = permission.get_object()
                        name = obj.name
                        target_name = permission.target_type.name
                    else:
                        name = '*'
                        target_name = '*'
                except ObjectDoesNotExist:
                    pass
                else:
                    key = '{}/{}'.format(target_name, name)
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

            return HttpResponse(json.dumps(content), content_type=JSON_CONTENT_TYPE)
        except ObjectDoesNotExist:
            return HttpResponseBadRequest(json.dumps({'error': 'invalid_token'}),
                                          content_type=JSON_CONTENT_TYPE)
