#! /usr/bin/python
# -*- coding: utf-8 -*-
"""
    apps.core.views
    ~~~~~~~~~

    :copyright: (c) 2015 by dorosh.
"""

__author__ = 'dorosh'
__date__ = '15.03.2015'

from django.shortcuts import redirect
from django.conf import settings
from django.views.generic.edit import FormView
from django.views.generic import View, ListView, TemplateView, DetailView
from django.http import JsonResponse
from django.contrib.auth import authenticate, login, get_user_model
from django.template.loader import render_to_string
from django.core.mail import send_mail
from django.core.urlresolvers import reverse

from registration.backends.default.views import RegistrationView, ActivationView
from registration.models import RegistrationProfile

from apps.core.utils import LoginRequiredMixin
from .forms import UserForm, LoginForm, RegUserForm, EmailForm

User = get_user_model()


class Login(FormView):

    form_class = LoginForm

    def post(self, request, *args, **kwargs):
        form = self.form_class(data=request.POST)
        return JsonResponse({
                'status': 'ok' if form.is_valid() else 'error',
                'form': render_to_string('forms/login_form.html', {'form': form})
                })


class EmailValidation(FormView):

    form_class = EmailForm
    template_name = 'login_form.html'

    def post(self, request, *args, **kwargs):
        form = self.form_class(data=request.POST)
        if form.is_valid():
            user = request.user
            user.email = form.cleaned_data.get("email")
            user.is_active = False
            user.save()

            site = get_site_model().objects.get_current()

            new_user = RegistrationProfile.objects.create_inactive_user(
                new_user=request.user,
                site=site,
                send_email=self.SEND_ACTIVATION_EMAIL,
                request=request,
            )
            signals.user_registered.send(sender=self.__class__,
                                         user=new_user,
                                         request=request)

        return JsonResponse({
                'status': 'ok' if form.is_valid() else 'error',
                'form': render_to_string('forms/login_form.html', {'form': form})
                })


class UserPage(LoginRequiredMixin, DetailView):

    context_object_name = 'person'
    template_name = 'public_profile.html'
    queryset = User.objects.all()


class MyRegistrationView(RegistrationView):

    form_class = RegUserForm

    def get_success_url(self, request=None, user=None):
        # We need to be able to use the request and the new user when
        # constructing success_url.
        username = request.POST.get('reg-username', '')
        password = request.POST.get('reg-password1', '')
        login(request, authenticate(username=username, password=password))
        return ('home', (), {})


class CustomActivationView(ActivationView):

    def get_success_url(self, request, user):
        return reverse('index')
