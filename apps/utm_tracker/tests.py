# coding: utf8

from django.contrib.sites.models import Site
from django.test.utils import override_settings
from django.test import TestCase, Client
from django.core.urlresolvers import reverse
from django.contrib.auth import get_user_model
from apps.utm_tracker.models import UTMUserTags
from apps.utm_tracker.middleware import utm_tags

User = get_user_model()


class TestUTMCookies(TestCase):
    def setUp(self):
        Site.objects.create(name='example.com', domain='example.com')
        self.client = Client()
        self.url = reverse('login')

    @override_settings(SET_COOKIE_DOMAIN=None)
    def test_dont_set_random_cookies(self):
        query = 'qwerty=123'
        resp = self.client.get(self.url + '?' + query)
        self.assertFalse(resp.cookies.has_key('qwerty'))
        self.register_user()
        self.assertEqual(UTMUserTags.objects.count(), 0)

    @override_settings(SET_COOKIE_DOMAIN=None)
    def test_setting_cookies(self):
        q = dict([(i, '123') for i in utm_tags])
        query = self.make_query(q)
        resp = self.client.get(self.url + '?' + query)
        self.assertTrue(resp.cookies.has_key('utm_tags'))
        self.register_user()
        self.assertEqual(UTMUserTags.objects.count(), 1)
        utm = UTMUserTags.objects.first()
        self.assertTrue(all(getattr(utm, i) == '123' for i in utm_tags))

    @override_settings(SET_COOKIE_DOMAIN=None)
    def test_setting_cookies_with_special_symbols(self):
        dic = {
            utm_tags[0]: u'йцу+кен',
            utm_tags[1]: '"qwe"',
        }
        query = self.make_query(dic)
        self.client.get(self.url + '?' + query)
        self.register_user()
        self.assertEqual(UTMUserTags.objects.count(), 1)
        utm = UTMUserTags.objects.first()
        self.assertEqual(getattr(utm, utm_tags[0]), dic[utm_tags[0]].replace('+', ' '))
        self.assertEqual(getattr(utm, utm_tags[1]), dic[utm_tags[1]])

    def register_user(self):
        url = reverse('registration_register2')
        reg_data = {'reg-username': 'username',
                    'reg-email': 'qwe@qwe.qwe',
                    'reg-password1': '123123',
                    'reg-password2': '123123'}
        resp = self.client.post(url, reg_data)
        self.assertEqual(resp.status_code, 302)

    def make_query(self, dic):
        s = ''
        for k,v in dic.iteritems():
            s += '%s=%s&' % (k, v)
        s = s[:-1]
        return s
