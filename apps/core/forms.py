#! /usr/bin/python
# -*- coding: utf-8 -*-
"""
    apps.forms.views
    ~~~~~~~~~

    :copyright: (c) 2015 by dorosh.
"""

__author__ = 'dorosh'
__date__ = '03.08.2015'

from django.core.exceptions import ObjectDoesNotExist
from django import forms
from django.contrib.auth import get_user_model

User = get_user_model()


class CreateUserForm(forms.Form):
    username = forms.CharField(max_length=30)
    first_name = forms.CharField()
    last_name = forms.CharField()
    password1 = forms.CharField(max_length=30, widget=forms.PasswordInput())
    password2 = forms.CharField(max_length=30, widget=forms.PasswordInput())
    email = forms.EmailField()

    def clean_username(self):
        try:
            User.objects.get(username=self.cleaned_data['username'])
        except ObjectDoesNotExist:
            return self.cleaned_data['username']
        raise forms.ValidationError("this user exist already")

    def clean(self):
        if 'password1' in self.cleaned_data and 'password2' in self.cleaned_data:
            if self.cleaned_data['password1'] != self.cleaned_data['password2']:
                raise forms.ValidationError("passwords dont match each other")
        return self.cleaned_data

    def save(self):
        new_user = User.objects.create_user(
            self.cleaned_data['username'],
            self.cleaned_data['email'],
            self.cleaned_data['password1']
        )
        new_user.first_name = self.cleaned_data['first_name']
        new_user.last_name = self.cleaned_data['last_name']
        new_user.save()
        return new_user
