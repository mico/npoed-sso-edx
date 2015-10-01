#! /usr/bin/python
# -*- coding: utf-8 -*-
import random
import requests
import urllib
import string

from django.core.exceptions import ObjectDoesNotExist
from django.http import JsonResponse
from django.contrib.auth import get_user_model
from django.contrib.auth.views import login as auth_login
from django.contrib.auth import REDIRECT_FIELD_NAME

from django.views.generic.edit import FormView
from django.views.generic import TemplateView, View
from django.shortcuts import redirect
from django.template.loader import render_to_string
from django.core.urlresolvers import reverse
from django.conf import settings

from provider.oauth2.models import Client, Grant

from .forms import CreateUserForm
from apps.profiler.forms import RegUserForm, LoginForm
from apps.core.utils import LoginRequiredMixin, SuperUserRequiredMixin


User = get_user_model()


def push_to_edx(user):
    #  Для использования функции из других приложений
    return _push_to_edx(user)


def _push_to_edx(user, success_url=None):
    """
    Специальный хак, чтоб активировать процесс логина/регистрации пользователя в edx
    через sso по инициативе sso
    Данную функцию следует вызывать например когда нужно в edx принудительно создать пользователя
    без его участия или засинхронизировать его роли
    """

    # вибираем текущий oauth клиент
    client = Client.objects.filter(redirect_uri=settings.EDX_CRETEUSER_URL)
    status_code = None
    if client:
        # создаем grant запись (второй шаг авторизации после проверки валидности запроса от клиента)
        grant = Grant.objects.create(
            user=user,
            client=client[0],
            redirect_uri=settings.EDX_CRETEUSER_URL,
            scope=2
        )
        params = {'state': ''.join(random.sample(string.ascii_letters, 32)),
                  'code': grant.code}
        # с этими параметрами возвращаемся на edx
        # дальше редиректы отработают по процессу oauth взаимодействия
        # и авторизационный бекенд создаст или засинкает пользователя
        r = requests.get(settings.EDX_CRETEUSER_URL, params, verify=False)  # не хотим проверять SSL сертификаты
        status_code = r.status_code
    if not success_url:
        return status_code
    else:
        return redirect(success_url)


def push_to_plp(user):
    #  Для использования функции из других приложений
    return _push_to_plp(user)


def _push_to_plp(user, success_url=None):
    """
    Специальный хак, чтоб активировать процесс логина/регистрации пользователя в plp
    через sso по инициативе sso
    Данную функцию следует вызывать например когда нужно в plp принудительно создать пользователя
    без его участия или засинхронизировать данные его профиля, в т.ч. email
    """

    # вибираем текущий oauth клиент
    client = Client.objects.filter(redirect_uri=settings.PLP_CRETEUSER_URL)
    status_code = None
    if client:
        # создаем grant запись (второй шаг авторизации после проверки валидности запроса от клиента)
        grant = Grant.objects.create(
            user=user,
            client=client[0],
            redirect_uri=settings.PLP_CRETEUSER_URL,
            scope=2
        )
        params = {'state': ''.join(random.sample(string.ascii_letters, 32)),
                  'code': grant.code}
        # с этими параметрами возвращаемся на plp
        # дальше редиректы отработают по процессу oauth взаимодействия
        # и авторизационный бекенд создаст или засинкает пользователя
        r = requests.get(settings.PLP_CRETEUSER_URL, params, verify=False)  # не хотим проверять SSL сертификаты
        status_code = r.status_code
    if not success_url:
        return status_code
    else:
        return redirect(success_url)


class Index(TemplateView):

    template_name = 'index.html'
    success_url = '/'

    def get(self, request, *args, **kwargs):

        get_next = request.GET.get('next', '')
        if request.user.is_authenticated():
            return redirect(reverse('profile'))
        elif get_next.split('auth_entry=')[-1] == 'register':
            return redirect('{}?next={}'.format(
                    reverse('registration_register2'),
                    urllib.pathname2url(get_next.split('auth_entry=')[0])
                    ))
        return redirect(settings.PLP_URL)

    def post(self, request, *args, **kwargs):
        form = RegUserForm(request.POST)
        return JsonResponse({
                'status': 'ok' if form.is_valid() else 'error',
                'reg_form': render_to_string('forms/form.html', {'form': form})
                })


class CreateManually(SuperUserRequiredMixin, FormView):
    """
    Въюшка с формой, которая позволяет создать нового пользователя в sso
    и тут же его засинкать в edx. Нужна была как минимум для демонстрации функционала
    """
    template_name = 'create_manually.html'
    form_class = CreateUserForm
    success_url = '/accounts/create_manually/'

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)
        if not form.is_valid():
            return super(CreateManually, self).get(request, *args, **kwargs)
        form.save()
        try:
            user = User.objects.get(email=form.cleaned_data['email'])
        except ObjectDoesNotExist:
            return redirect(self.success_url)
        return _push_to_edx(user, self.success_url)


class EdxPush(LoginRequiredMixin, View):
    """
    Вьюшка для обработки синхронизации существующего sso-пользователя на edx
    """
    success_url = '/profile/'

    def get(self, request, *args, **kwargs):
        try:
            user = User.objects.get(id=kwargs['pk'])
        except ObjectDoesNotExist:
            return redirect(self.success_url)
        return _push_to_edx(user, self.success_url)


def login(request, template_name='registration/login.html',
          redirect_field_name=REDIRECT_FIELD_NAME,
          authentication_form=LoginForm,
          current_app=None, extra_context=None):
    if request.user.is_authenticated():
        return redirect(settings.PLP_URL)
    # проверка параметра auth_entry, чтоб отредиректить на форму регистрации если такова запрошена
    # с сохранением всех get параметров для нормального продолжение oauth авторизации через регистрацию
    get_next = request.GET.get('next', '')    
    if get_next.split('auth_entry=')[-1] == 'register':
        return redirect('{}?next={}'.format(
                reverse('registration_register2'),
                urllib.pathname2url(get_next.split('auth_entry=')[0])
            ))
    return auth_login(request, authentication_form=LoginForm)
