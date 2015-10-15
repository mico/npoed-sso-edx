#! /usr/bin/python
# -*- coding: utf-8 -*-

from urllib import urlopen
from datetime import datetime
from unidecode import unidecode

from django.core.files.storage import default_storage
from django.shortcuts import redirect
from django.core.files.base import ContentFile

from social.pipeline.partial import partial

from apps.core.utils import make_random_password
from apps.profiler.models import User


def update_details(details, *args, **kwargs):

    response = kwargs.get('response', {})
    backend = kwargs.get('backend', {})
    gender_dict = {1: u'мужской', 2: u'женский'}
    change_data = False
    image_url = None
    out = {}

    if backend.name == 'vk-oauth2':
        out['image_url'] = response.get('photo_100')
        out['gender'] = response.get('sex')#{2: 'male', 1: 'female'}.get(response.get('sex'))
        out['bdate'] = response.get('bdate')

    elif backend.name == 'facebook':
        out['image_url'] = 'http://graph.facebook.com/{0}/picture?type=normal'.format(response['id'])
        out['gender'] = gender_dict.get(response.get('gender'))

    elif backend.name == 'twitter':
        out['image_url'] = response.get('profile_image_url')
        out['country'] = response.get('country')

    elif backend.name == 'google-oauth2':
        out['gender'] = gender_dict.get(response.get('gender'))

    elif backend.name == 'mailru-oauth2':
        out['gender'] = {0: u'мужской', 1: u'женский'}.get(response.get('sex'))
        out['birthday'] = response.get('birthday')
        out['image_url'] = response.get('pic_32')

    details.update(out)


@partial
def require_email(strategy, details, user=None, is_new=False, *args, **kwargs):

    if kwargs:
        update_details(details, **kwargs)
    if kwargs.get('ajax') or user and user.email:
        return
    elif is_new:
        first_email = details.get('email')
        email = strategy.request_data().get('email')
        if email and first_email != email:
            details['email'] = email
            details['validation'] = True
        elif email and first_email == email:
            return
        else:
            return redirect('require_email')


@partial
def mail_validation(backend, details, is_new=False, *args, **kwargs):
    requires_validation = backend.REQUIRES_EMAIL_VALIDATION or \
                          backend.setting('FORCE_EMAIL_VALIDATION', False)
    send_validation = details.get('email') and \
                      (is_new or backend.setting('PASSWORDLESS', False)) and details.get('validation')
    if requires_validation and send_validation:
        data = backend.strategy.request_data()
        if 'verification_code' in data:
            backend.strategy.session_pop('email_validation_address')
            if not backend.strategy.validate_email(details['email'],
                                           data['verification_code']):
                raise InvalidEmail(backend)
        else:
            backend.strategy.send_email_validation(backend, details['email'])
            backend.strategy.session_set('email_validation_address',
                                         details['email'])
            return backend.strategy.redirect(
                backend.strategy.setting('EMAIL_VALIDATION_URL')
            )


@partial
def update_profile(backend, user, response, *args, **kwargs):

    if user is None or not response:
        return

    gender_dict = {u'мужской': 1, u'женский': 2}
    change_data = False
    image_url = None

    if backend.name == 'vk-oauth2':
        image_url = response.get('photo_100')
        gender = response.get('sex')
        if not user.gender and gender:
            change_data = True
            # in vk male has id 2, female has id 1
            user.gender = {2: 1, 1: 2, u'мужской': 1, u'женский': 2}.get(gender)

        bdate = response.get('bdate')
        if not user.date_of_birth and bdate:
            try:
                bdate = datetime.strptime(bdate, "%d.%m.%Y").date()
            except Exception:
                pass
            else:
                user.date_of_birth = bdate
                change_data = True

    elif backend.name == 'facebook':
        image_url = 'http://graph.facebook.com/{0}/picture?type=normal'.format(response['id'])
        gender = response.get('gender')
        if not user.gender and gender:
            change_data = True
            user.gender = gender_dict.get(gender)

    elif backend.name == 'twitter':
        image_url = response.get('profile_image_url')
        country = response.get('country')
        if not user.country and country:
            change_data = True
            user.country = country

    elif backend.name == 'google-oauth2':

        gender = response.get('gender')
        if not user.gender and gender:
            change_data = True
            user.gender = gender_dict.get(gender)

    elif backend.name == 'mailru-oauth2':

        gender = response.get('sex')
        print 
        if not user.gender and gender:
            change_data = True
            # in mailru male has id 0, female has id 1
            user.gender = {0: 1, 1: 2, u'мужской': 1, u'женский': 2}.get(gender)

        birthday = response.get('birthday')
        if not user.date_of_birth and birthday:
            try:
                birthday = datetime.strptime(birthday, "%d.%m.%Y").date()
            except ValueError:
                pass
            else:
                user.date_of_birth = birthday
                change_data = True

    if change_data:
        user.save()

    if not user.has_usable_password():
        user.set_password(make_random_password())
        user.save()

    if image_url and not user.icon_profile:
        try:
            image_content = urlopen(image_url)
            image_name = '.'.join([str(user.id), image_content.headers.subtype])
            user.icon_profile.save(image_name, ContentFile(image_content.read()))
            user.save()
        except Exception:
            pass


@partial
def get_entries(strategy, user, name, user_storage, association_id=None, *args, **kwargs):
    entries = user_storage.get_social_auth_for_user(user, name, association_id)
    if user_storage.get_social_auth_for_user(user).count() == 1:
        strategy.session_set('last_social', 1)
    else:
        strategy.session_pop('last_social')
    return {'entries': entries}


@partial
def get_username(strategy, details, user=None, *args, **kwargs):
    username = details.get('username', '')
    if username:
        try:
            username = unidecode(username).replace(' ', '')
        except:
            pass

        try:
            users = User.objects.get(username=username)
        except User.DoesNotExist:
            pass
        else:
            users = User.objects.filter(username__icontains=username).count()
            username = '{}{}'.format(username, users + 1)

        return {'username': username}
