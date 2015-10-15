#! /usr/bin/python
# -*- coding: utf-8 -*-

from django import forms
from django.utils.safestring import mark_safe
from django.contrib.auth.forms import (
    AuthenticationForm, PasswordResetForm, SetPasswordForm, PasswordChangeForm
)
from django.contrib.auth import get_user_model
from django.core import validators
from django.conf import settings

from registration.forms import RegistrationFormUniqueEmail
from django_countries import countries

User = get_user_model()


class UserForm(forms.ModelForm):

    about_me = forms.CharField(widget=forms.Textarea(attrs={
        'style': 'width: 100%;'}), required=False, label=u'О себе')
    username = forms.CharField(widget=forms.TextInput(
            attrs={'class':'disabled', 'readonly':'readonly'}), label=u'Логин')
    email = forms.EmailField(label=u'Адрес e-mail')
    last_name = forms.CharField(label=u'Фамилия')
    first_name = forms.CharField(label=u'Имя')

    date_of_birth = forms.DateField(label=u'Дата рождения',
            widget=forms.TextInput(attrs={'class': 'vDateField'}), required=False)

    class Meta:
        model = User
        fields = [
            'username', 'email', 'last_name', 'first_name', 'second_name',
            'icon_profile', 'gender', 'date_of_birth', 'education', 'university',
            'country', 'city', 'post_address', 'phone', 'about_me'
        ]

    # sort countries by translate name
    def __init__(self, *args, **kwargs):
        super(UserForm, self).__init__(*args, **kwargs)
        list_countries = list(countries)
        first = []
        if hasattr(settings, 'COUNTRIES_FIRST'):
            for country in settings.COUNTRIES_FIRST:
                ind = [element[0] for element in list_countries].index(country)
                first.append(list_countries[ind])
                list_countries.pop(ind)
        self.fields['country'].choices = first + sorted(
            list_countries,
            key=lambda list_countries: list_countries[1])

    def clean_email(self):
        email = self.cleaned_data['email']
        username = self.cleaned_data['username']
        if User.objects.exclude(username=username).filter(email=email).exists():
            raise forms.ValidationError(u'Этот e-mail уже используется')
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            raise forms.ValidationError(u'Неправильный логин')
        else:
            if user.email != email:
                msg = u'''
                       На почту {} было отправлено письмо
                       для активации нового e-mail
                      '''.format(email)
                raise forms.ValidationError(msg)
        return email

    def clean_first_name(self):
        first_name = self.cleaned_data.get('first_name')
        if len(first_name) > 30:
            raise forms.ValidationError(
                u'Имя слишком длинное, максимальная длина 30')
        return first_name

    def clean_last_name(self):
        last_name = self.cleaned_data.get('last_name')
        if len(last_name) > 30:
            raise forms.ValidationError(
                u'Фамилия слишком длинная, максимальная длина 30')
        return last_name

    def clean_second_name(self):
        second_name = self.cleaned_data.get('second_name')
        if len(second_name) > 30:
            raise forms.ValidationError(
                u'Отчество слишком длинное, максимальная длина 30')
        return second_name


class RegUserForm(RegistrationFormUniqueEmail):

    email = forms.EmailField(label=u'Почта')
    password1 = forms.CharField(label=u'Пароль', widget=forms.PasswordInput())
    password2 = forms.CharField(label=u'Повторите', widget=forms.PasswordInput())
    username = forms.CharField(
        label=u'Логин', validators=[
            validators.RegexValidator('^[-a-zA-Z0-9_]+$',
                                      message=u'Вы можете использовать латинские символы, цифры и _'),
            validators.MinLengthValidator(3)
        ]
    )

    def __init__(self, *args, **kwargs):
        kwargs['prefix'] = 'reg'
        super(RegUserForm, self).__init__(*args, **kwargs)

    def clean_email(self):
        data = self.cleaned_data['email']
        if User.objects.filter(email=data).exists():
            raise forms.ValidationError(u'Этот e-mail уже используется')
        return data

    def clean_password1(self):
        password = self.cleaned_data.get('password1')
        if len(password) < settings.MIN_LENGTH_PASSWORD:
            raise forms.ValidationError(
                u'Пароль слишком короткий, минимальная длина %s' % settings.MIN_LENGTH_PASSWORD)
        return password

    class Meta:
        prefix = 'reg'
        model = User
        fields = ['email', 'password1', 'password2', 'username']


class LoginForm(AuthenticationForm):

    password = forms.CharField(
        label=u'Пароль', widget=forms.PasswordInput(attrs={
                "class": "span12", "placeholder": "", "tabindex": "1"}))
    username = forms.CharField(
        label=u'Логин', widget=forms.TextInput(attrs={
                "class": "span12", "placeholder": "", "tabindex": "1"}))

    def confirm_login_allowed(self, user):
        pass

    def clean(self):
        cleaned_data = super(LoginForm, self).clean()
        try:
            user = User.objects.get(username=cleaned_data.get("username"))
        except User.DoesNotExist:
            raise forms.ValidationError(u'Неправильный логин')
        if not user.is_active:
            raise forms.ValidationError(u'Этот аккаунт не активирован')


class CustomPasswordResetForm(PasswordResetForm):

    # Check exist email
    def clean_email(self):
        email = self.cleaned_data['email']
        if not User.objects.filter(email=email).exists():
            raise forms.ValidationError(u'Пользователь с такой почтой не найден')
        return email


class CustomSetPasswordForm(SetPasswordForm):

    def clean_new_password1(self):
        password = self.cleaned_data.get('new_password1')
        if len(password) < settings.MIN_LENGTH_PASSWORD:
            raise forms.ValidationError(
                u'Пароль слишком короткий, минимальная длина %s' % settings.MIN_LENGTH_PASSWORD)
        return password


class CustomPasswordChangeForm(PasswordChangeForm):

    def clean_new_password1(self):
        password = self.cleaned_data.get('new_password1')
        if len(password) < settings.MIN_LENGTH_PASSWORD:
            raise forms.ValidationError(
                u'Пароль слишком короткий, минимальная длина %s' % settings.MIN_LENGTH_PASSWORD)
        return password
# TODO DRY ^
