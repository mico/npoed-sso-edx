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
from django.views.generic import TemplateView, View
from django.shortcuts import redirect
from django.template.loader import render_to_string
from django.core.urlresolvers import reverse
from django.conf import settings

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


def _push_to_edx(user, success_url):
    client = Client.objects.filter(redirect_uri=settings.EDX_CRETEUSER_URL)
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
    return redirect(success_url)


class Index(TemplateView):

    template_name = 'index.html'
    success_url = '/'

    def get(self, request, *args, **kwargs):

        get_next = request.GET.get('next', '')
        if request.user.is_authenticated():
            return redirect(reverse('home'))
        elif get_next.split('auth_entry=')[-1] == 'register':
            return redirect('{}?next={}'.format(
                    reverse('registration_register2'),
                    urllib.pathname2url(get_next.split('auth_entry=')[0])
                    ))
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
        return _push_to_edx(user, self.success_url)


class EdxPush(LoginRequiredMixin, View):

    success_url = '/profile/'

    def get(self, request, *args, **kwargs):
        print args, kwargs
        try:
            user = User.objects.get(id=kwargs['pk'])
        except ObjectDoesNotExist:
            return redirect(self.success_url)
        return _push_to_edx(user, self.success_url)
