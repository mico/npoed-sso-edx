#! /usr/bin/python
# -*- coding: utf-8 -*-

from social.backends.oauth import BaseOAuth2


class NpoedBackend(BaseOAuth2):
    name = 'community-npoed'
    ID_KEY = 'user_id'
    AUTHORIZATION_URL = 'http://community.npoed.ru/oauth/authorize'
    ACCESS_TOKEN_URL = 'http://community.npoed.ru/oauth/token'
    DEFAULT_SCOPE = []
    REDIRECT_STATE = False
    ACCESS_TOKEN_METHOD = 'POST'

    def get_user_details(self, response):
        """ Return user details from NPOED account. """
        email = response.get('email', '')
        firstname = response.get('firstname', '')
        lastname = response.get('lastname', '')
        fullname = ' '.join([firstname, lastname])
        return {'username': email.split('@', 1)[0],
                'email': email,
                'fullname': fullname,
                'first_name': firstname,
                'last_name': lastname}

    def user_data(self, access_token, *args, **kwargs):
        """ Grab user profile information from NPOED. """
        userinfo = self.get_json('http://community.npoed.ru/api/me',
                                 params={'access_token': access_token})
        email = userinfo['email']
        return {
            'user_id': userinfo['id'],
            'username': email.split('@', 1)[0],
            'email': email,
            'firstname': userinfo['name'],
            'lastname': userinfo['surname'],
        }

    def do_auth(self, access_token, *args, **kwargs):
        """Finish the auth process once the access_token was retrieved"""
        data = self.user_data(access_token)
        data['access_token'] = access_token
        kwargs.update({'response': data, 'backend': self})
        return self.strategy.authenticate(*args, **kwargs)
