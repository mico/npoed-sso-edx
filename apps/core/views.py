import requests
import json

from django.views.generic import TemplateView
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponseBadRequest, HttpResponse

from provider.oauth2.views import AccessTokenDetailView
from provider.oauth2.models import AccessToken



from django import forms
from django.contrib.auth.models import User
from django.views.generic.edit import FormView
from django.shortcuts import redirect

from provider.oauth2.models import Client, AccessToken, Grant


url = 'http://rnoep.raccoongang.com/auth/complete/sso_npoed-oauth2/'


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
        except User.DoesNotExist :
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


class Home(FormView):

    template_name = 'index.html'
    form_class = CreateUserForm
    success_url = '/'

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
            # AccessToken.objects.create(
            #     user=user,
            #     client=client[0],
            #     scope=2
            # )
            grant = Grant.objects.create(
                user=user,
                client=client[0],
                redirect_uri=url,
                scope=2
            )
            r = requests.get(url + '?state=FntJ1v4fBr16sRqsH4N6fph2CXT4BEB7&code=' + grant.code)
            print r.text
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
                'scope': access_token.get_scope_display(),
                'expires': access_token.expires.isoformat()
            }
            return HttpResponse(json.dumps(content), content_type=JSON_CONTENT_TYPE)
        except ObjectDoesNotExist:
            return HttpResponseBadRequest(json.dumps({'error': 'invalid_token'}),
                                          content_type=JSON_CONTENT_TYPE)
