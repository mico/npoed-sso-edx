#! /usr/bin/python
# -*- coding: utf-8 -*-
import base64
import urllib
import random
import logging

from django.conf import settings
from django.views.generic import TemplateView
from django.views.generic.edit import FormView, UpdateView
from django.http import HttpResponseBadRequest, JsonResponse, Http404
from django.contrib.auth import login, get_user_model
from django.template.loader import render_to_string
from django.contrib.sites.models import Site, RequestSite
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.shortcuts import redirect
from django.contrib.sessions.backends.db import SessionStore
from django.contrib.auth import logout
from django.core.validators import validate_email
from django.utils.http import urlsafe_base64_encode
from django.contrib.auth.tokens import default_token_generator
from django.utils.encoding import force_bytes
from django.template import loader
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import send_mail

from social.backends.oauth import BaseOAuth1, BaseOAuth2
from social.backends.google import GooglePlusAuth
from social.backends.utils import load_backends
from social.apps.django_app.utils import psa
from social.utils import setting_name

from registration.backends.default.views import (
    ActivationView, RegistrationView as RW
)
from registration import signals
from rest_framework import permissions
from rest_framework.views import APIView
from rest_framework.response import Response

from apps.core.utils import LoginRequiredMixin, decrypt
from apps.core.decorators import render_to
from apps.profiler.forms import UserForm, LoginForm, RegUserForm, EmailForm
from apps.profiler.models import RegistrationProfile, send_change_email
from apps.permissions.models import Permission
from apps.openedx_objects.models import (
    EdxCourse, EdxCourseRun, EdxOrg, EdxLibrary
)
from raven import Client

NAMESPACE = getattr(settings, setting_name('URL_NAMESPACE'), None) or 'social'
RAVEN_CONFIG = getattr(settings, 'RAVEN_CONFIG', {})
client = None

if RAVEN_CONFIG:
    client = Client(RAVEN_CONFIG.get('dsn'))

User = get_user_model()


class ApiKeyPermission(permissions.BasePermission):
    '''
    Check Api key
    '''
    def has_permission(self, request, view):
        api_key = getattr(settings, 'SSO_API_KEY', None)
        if not api_key:
            logging.error('SSO_API_KEY not configured')
        key = request.META.get('HTTP_X_SSO_API_KEY')
        if key and api_key and key == api_key:
            return True
        return False


class UserMassRegistration(APIView):
    '''
    Массовая регистрация пользователей по списку емейлов и slug университета
    '''
    permission_classes = (ApiKeyPermission,)
    email_subject = 'registration/password_set_subject.txt'
    email_html = 'registration/password_set_email.html'

    def post(self, request, **kwargs):
        emails = request.data.get('emails')
        university = request.data.get('university')
        if not university:
            return Response({'errors': ['University slug must be specified']})
        users = []
        if emails and isinstance(emails, list):
            make_active = []
            for email in emails:
                try:
                    validate_email(email)
                except:
                    continue

                users_q = User.objects.filter(email=email)
                if users_q:
                    user = users_q[0]
                    users.append({'email': email, 'username': user.username})
                else:
                    username = '%s_%s' % (university, email.split('@')[0])
                    while User.objects.filter(username=username).exists():
                        username += str(random.randint(0, 9))
                    password = User.objects.make_random_password()
                    user = User.objects.create_user(username, email, password)
                    make_active.append(user.id)
                    users.append({'email': email, 'username': user.username})
                    current_site = get_current_site(None)
                    c = {
                        'email': user.email,
                        'domain': current_site.domain,
                        'site_name': current_site.name,
                        'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                        'user': user,
                        'token': default_token_generator.make_token(user),
                        'protocol': settings.URL_PREFIX,
                    }
                    subject = loader.render_to_string(self.email_subject, c)
                    subject = ''.join(subject.splitlines())
                    send_mail(subject,
                              loader.render_to_string(self.email_html, c),
                              settings.DEFAULT_FROM_EMAIL,
                              [user.email])
            User.objects.filter(id__in=make_active).update(is_active=True)

        else:
            return Response({'errors': ['Emails should be non-empty list']})
        return Response({'users': users})


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
                    if permission.target_type.model == EdxCourseRun._meta.verbose_name:
                        obj = permission.target_type.model_class().objects.get(
                            pk=permission.target_id
                        )
                        name = obj.course.course_id
                    elif permission.target_type.model in [
                        EdxCourse._meta.verbose_name, EdxLibrary._meta.verbose_name]:
                        obj = permission.target_type.model_class().objects.get(
                            pk=permission.target_id
                        )
                        name = obj.course_id
                    elif permission.target_type.model == EdxOrg._meta.verbose_name:
                        obj = permission.target_type.model_class().objects.get(
                            pk=permission.target_id
                        )
                        name = obj.name
                    else:
                        msg = 'None'
                        if permission.target_type:
                            msg = permission.target_type.model
                        if client:
                            client.captureMessage(
                                'This object is not permited: {}'.format(msg)
                            )
                        continue
                else:
                    if permission.target_id:
                        continue
                    name = '*'
                target_name = permission.target_type.model
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


class EmailValidation(FormView):

    form_class = EmailForm

    def post(self, request, *args, **kwargs):
        form = self.form_class(data=request.POST)
        return JsonResponse({
                'status': 'ok' if form.is_valid() else 'error',
                'form': render_to_string('forms/email_form.html', {'form': form})
                })


class Profile(LoginRequiredMixin, UpdateView):

    template_name = 'profile.html'
    form_class = UserForm
    success_url = '/profile/'
    model = User

    def get_context_data(self, **kwargs):
        context = super(Profile, self).get_context_data(**kwargs)
        context['last_social'] = self.request.session.get('last_social', 0)
        if context['last_social']:
            self.request.session.pop('last_social')
        return context

    def get_object(self, queryset=None):
        return self.request.user

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        form_class = self.get_form_class()
        form = self.get_form(form_class)
        if form.is_valid():
            return self.form_valid(form)
        else:
            email = request.POST.get('email')
            if Site._meta.installed:
                site = Site.objects.get_current()
            else:
                site = RequestSite(request)
            if email != self.object.email:
                send_change_email(self.object, email, site, request=request)
            return self.form_invalid(form)


class RegistrationView(RW):

    form_class = RegUserForm

    def get_success_url(self, request=None, user=None):
        # We need to be able to use the request and the new user when
        # constructing success_url.
        return ('registered', (), {})

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


class RegisteredView(TemplateView):

    template_name = 'registration/registered.html'


class CustomActivationView(ActivationView):

    template_name = 'registration/activation_complete.html'

    def get(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        activated_user = self.activate(request, *args, **kwargs)
        if request.GET.get('next'):
            context['next'] = request.GET.get('next')

        if activated_user:
            context['activated_user'] = True
            context['username'] = activated_user.username
            bind_social = '{}?next={}'.format(
                reverse('bind_social'),
                urllib.pathname2url(request.GET.get('next', ''))
            )

            return redirect(bind_social)
        return self.render_to_response(context)


class BindSocialView(LoginRequiredMixin, TemplateView):

    template_name = 'registration/bind_social.html'

    def get(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        if request.GET.get('next'):
            context['next'] = request.GET.get('next')
            request.session['next_past_bind'] = request.GET.get('next')
        elif request.session.get('next_past_bind'):
            context['next'] = request.session.get('next_past_bind')
        return self.render_to_response(context)


@login_required
@render_to('registration/registration_form.html')
def done(request):
    """Login complete view, displays user data"""
    return context()


@render_to('registration/registration_form.html')
def validation_sent(request):
    if request.session.get('email_validation_address'):
        return context(
            validation_sent=True,
            email=request.session.get('email_validation_address')
        )
    else:
        raise Http404


@render_to('registration/email.html')
def require_email(request):
    try:
        details = request.session['partial_pipeline']['kwargs']['details']
        form = EmailForm(initial={'email': details['email']})
        backend = request.session['partial_pipeline']['backend']
    except KeyError:
        raise Http404
    return context(email_required=True, backend=backend, form=form, **details)


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
    return JsonResponse({'id': user.id, 'username': user.username})


def email_complete(request, backend, *args, **kwargs):
    """Authentication complete view"""
    verification_code = decrypt(request.GET.get('verification_code', ''))
    if '||' in verification_code:
        verification_code, session_key = verification_code.split('||')
        session_key = base64.b64decode(session_key)
        session = SessionStore(session_key)
        if request.session.session_key != session_key:
            logout(request)

        request.session.update(dict(session.items()))

    redirect_value = request.session.get('next', '')

    url = '{0}?verification_code={1}&next={2}'.format(
        reverse('social:complete', args=(backend,)),
        verification_code, redirect_value
    )
    request.session.update({'next': reverse('bind_social'),
                            'next_past_bind': redirect_value})
    return redirect(url)


def email_change(request, *args, **kwargs):
    """Authentication complete view"""
    try:
        key = request.GET.get('activation_key', '')
        if len(key) > 1:
            activation_key = decrypt(key[:-1])
    except TypeError:
        return redirect(reverse('incorrect_key'))
    if '||' in activation_key:
        pk, email, rand_val = activation_key.split('||')
        try:
            user = User.objects.get(pk=pk)
            user.email = email
            user.save()
        except User.DoesNotExist:
            raise Http404

    return redirect(reverse('profile'))


class IncorrectKeyView(TemplateView):

    template_name = 'registration/incorrect_activation_key.html'
