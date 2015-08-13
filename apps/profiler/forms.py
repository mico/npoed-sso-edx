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

from registration.forms import RegistrationFormUniqueEmail

# from .models import User
from django.contrib.auth import get_user_model

User = get_user_model()


class MessageForm(forms.Form):
    name = forms.CharField(
        label='', widget=forms.TextInput(
            attrs={"class": "span12", "id":"contact-name",
                   "placeholder": "Name"}))
    email = forms.EmailField(label='', widget=forms.TextInput(
            attrs={"class": "span12", "id": "contact-email",
                   "placeholder": "Email address"}))
    text = forms.CharField(label='', widget=forms.Textarea(
            attrs={"class": "span12", "rows": "5", "id": "contact-msg",
                   "placeholder": "Send us your questions or comments!"}))


class TextInput(forms.TextInput):
    '''
    '''

    def render(self, name, value, attrs=None):
        output = ''
        output_item = '''
	  <h4 id="myModalLabel" class="label_nineID">Choose a unique Username:</h4>
          <span class="nineID">@</span>%s
            '''
        output = output_item % super(TextInput, self).render(
            name, value, attrs=attrs)
        return mark_safe(output)


class CustomTextInput(forms.TextInput):
    '''
    '''

    def render(self, name, value, attrs=None):
        print name, value, attrs
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
        output = '<p>Sex</p>%s' % super(SexRadio, self).render(
            name, value, attrs=attrs)
        return mark_safe(output.replace('ul ', 'ul class="form-inline" '))


class SubscribeRadio(forms.RadioSelect):

    def render(self, name, value, attrs=None):
        output = '<p>Subscribe to updates and special offers</p>%s' % super(
            SubscribeRadio, self).render(name, value, attrs=attrs)
        return mark_safe(output.replace('ul ', 'ul class="form-inline" '))


class UserForm(forms.ModelForm):

    class Meta:
        model = User
        fields = [
            'email', 'username', 'first_name', 'last_name', 'role', 'education',
            'university_group', 'university', 'post_address', 'city', 'country',
            'phone', 'time_zone', 'icon_profile', 'date_of_birth', 'gender',
            'second_name']


class RegUserForm(RegistrationFormUniqueEmail):#(forms.ModelForm):

    email = forms.EmailField(
        label='', widget=forms.TextInput(
            attrs={"class": "span12", "placeholder": "Email address"}))
    password1 = forms.CharField(
        label='', widget=forms.PasswordInput(attrs={
                "class": "span12", "placeholder": "Password"}))
    password2 = forms.CharField(label='', widget=forms.HiddenInput())
    username = forms.CharField(label='', widget=forms.HiddenInput())

    def __init__(self, *args, **kwargs):
        kwargs['prefix'] = 'reg'
        super(RegUserForm, self).__init__(*args, **kwargs)

    def clean_email(self):
        data = self.cleaned_data['email']
        if User.objects.filter(email=data).exists():
            raise forms.ValidationError("This email already used")
        return data

    class Meta:
        prefix = 'reg'
        model = User
        fields = ['email', 'password1', 'password2', 'username']


class LoginForm(AuthenticationForm):

    password = forms.CharField(
        label='', widget=forms.PasswordInput(attrs={
                "class": "span12", "placeholder": "Password"}))
    username = forms.CharField(widget=CustomTextInput())

    def confirm_login_allowed(self, user):
        pass

    def clean(self):
        cleaned_data = super(LoginForm, self).clean()
        try:
            user = User.objects.get(username=cleaned_data.get("username"))
        except:
            raise forms.ValidationError("Invalid username")
        if not user.is_active:
            raise forms.ValidationError("This account is inactive.")
