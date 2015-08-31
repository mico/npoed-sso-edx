#! /usr/bin/python
# -*- coding: utf-8 -*-
"""
    apps.profiler.forms
    ~~~~~~~~~

    :copyright: (c) 2015 by dorosh.
"""

__author__ = 'dorosh'
__date__ = '15.03.2015'

from django import forms
from django.utils.safestring import mark_safe
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import get_user_model
from django.core import validators
from django.conf import settings

from registration.forms import RegistrationFormUniqueEmail

User = get_user_model()


class MessageForm(forms.Form):
    name = forms.CharField(
        label='', widget=forms.TextInput(
            attrs={"class": "span12", "id":"contact-name",
                   "placeholder": u'Имя'}))
    email = forms.EmailField(label='', widget=forms.TextInput(
            attrs={"class": "span12", "id": "contact-email",
                   "placeholder": u'Адрес e-mail'}))
    text = forms.CharField(label='', widget=forms.Textarea(
            attrs={"class": "span12", "rows": "5", "id": "contact-msg",
                   "placeholder": u'Ваш вопрос или предложение'}))


class TextInput(forms.TextInput):
    '''
    '''

    def render(self, name, value, attrs=None):
        output = ''
        output_item = '''
	  <h4 id="myModalLabel" class="label_nineID">Выберите уникальное имя пользователя:</h4>
          <span class="nineID">@</span>%s
            '''
        output = output_item % super(TextInput, self).render(
            name, value, attrs=attrs)
        return mark_safe(output)


class CustomTextInput(forms.TextInput):
    '''
    '''

    def render(self, name, value, attrs=None):
        #<input class="span12" id="id_username" maxlength="254" name="username" placeholder="9ineID / Email address" type="text">
        # output = ''
        # output_item = '''
        #     <div class="form-group">
        #       <label for="inputPassword3" class="col-sm-3 control-label">Nickname</label>
        #       <div class="col-sm-9">
        #         <input type="text" class="form-control" id="inputPassword3" placeholder="Nickname">
        #       </div>
        #     </div>
        #     '''
        # output = output_item % super(TextInput, self).render(
        #     name, value, attrs=attrs)
        # return mark_safe(output)
        return super(CustomTextInput, self).render(name, value, attrs=attrs)


class DateInput(forms.DateInput):
    '''
    '''

    def render(self, name, value, attrs=None):
        output = '''
	  <p>Date of Birth</p>
	  <div class="form-inline">
	    <input class="span3" id="day" type="tel" maxlength="2" placeholder="DD" value="%s"/>
	    <input class="span3" id="month" type="tel" maxlength="2" placeholder="MM" value="%s"/>
	    <input class="span4" id="year" type="tel" maxlength="4" placeholder="YYYY" value="%s"/>
	    <input type="hidden" id="id_date_of_birth" name="date_of_birth" value="%s"/>
	  </div>
            '''
        if value and not isinstance(value, basestring):
            value = value.strftime('%m/%d/%Y')
        params = ('', '', '', '',) if not value else tuple(value.split('/') + [value])
        return mark_safe(output % params)


class SexRadio(forms.RadioSelect):

    def render(self, name, value, attrs=None):
        output = '<p>Пол</p>%s' % super(SexRadio, self).render(
            name, value, attrs=attrs)
        return mark_safe(output.replace('ul ', 'ul class="form-inline" '))


class SubscribeRadio(forms.RadioSelect):

    def render(self, name, value, attrs=None):
        output = '<p>Подписаться на рассылку</p>%s' % super(
            SubscribeRadio, self).render(name, value, attrs=attrs)
        return mark_safe(output.replace('ul ', 'ul class="form-inline" '))


class UserForm(forms.ModelForm):

    about_me = forms.CharField(widget=forms.Textarea(attrs={
        'style': 'width: 100%;'}), required=False)
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
            'country', 'city', 'post_address', 'phone', 'about_me',
        ]

class RegUserForm(RegistrationFormUniqueEmail):

    email = forms.EmailField(label=u'Почта')
    password1 = forms.CharField(label=u'Пароль', widget=forms.PasswordInput())
    password2 = forms.CharField(label=u'Повторите', widget=forms.PasswordInput())
    username = forms.CharField(
        label=u'Имя', validators=[
            validators.RegexValidator('^[-a-zA-Z0-9_]+$'),
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
        label=u'Имя пользователя', widget=CustomTextInput(attrs={
                "class": "span12", "placeholder": "", "tabindex": "1"}))

    def confirm_login_allowed(self, user):
        pass

    def clean(self):
        cleaned_data = super(LoginForm, self).clean()
        try:
            user = User.objects.get(username=cleaned_data.get("username"))
        except:
            raise forms.ValidationError(u'Неправильное имя пользователя')
        if not user.is_active:
            raise forms.ValidationError(u'Этот аккаунт не активирован')
