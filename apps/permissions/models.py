#! /usr/bin/python
# -*- coding: utf-8 -*-

from django.db import models
from django.contrib.contenttypes.models import ContentType

from provider.oauth2.models import Client


class Permission(models.Model):
    '''
    Модель для хранения прав на доступ к объектам.
    Права могут общими:
        Все права на все объекты (админ): action_type='*', target_type=None, target_id=None
        Все права на конкретный объект:
            Org-staff: action_type='*', target_type=org, target_id=1
            Course-staff: action_type='*', target_type=course, target_id=1
        Права на чтение на конкретный объект: action_type='Read', target_type=course, target_id=1

    Потом конкретные права (один или несколько) назначаются роли, а роли назначается пользователю.
    '''

    action_choices = (
        ('*', '*', ),
        ('Read', 'Read', ),
        ('Update', 'Update', ),
        ('Manage(permissions)', 'Manage(permissions)', ),
        ('Delete', 'Delete', ),
        ('DownLoad', 'DownLoad', ),
        ('Archive', 'Archive', ),
        ('Create', 'Create', ),
        ('Publication', 'Publication', ),
        ('Enroll', 'Enroll', ),
    )

    action_type = models.CharField(
        max_length=50, choices=action_choices, blank=True, null=True
    )
    target_type = models.ForeignKey(
        ContentType, limit_choices_to={'app_label': u'openedx_objects'},
        related_name='content_types',
        blank=True, null=True
    )
    target_id = models.PositiveIntegerField(
        blank=True, null=True
    )

    def __unicode__(self):
        target_type = '*' if not self.target_type else self.target_type.name
        return '%s/%s/%s' % (self.action_type, target_type, self.target_id or '*', )

    def get_object(self, default=None):
        cls = self.target_type.model_class()

        try:
            return cls.objects.get(pk=self.target_id)
        except cls.DoesNotExist:
            return default

class Role(models.Model):
    '''
    К данной модели группируются права. На эту модель ссылается пользователь.
    У пользователя может быть много ролей.

    Соответствие наборов прав ролям пользователям на Open edX:
    https://docs.google.com/document/d/1QTTso8MntthcO7DJZHqFjS2KXc7mTpT16LTT53uFUIU/edit
    '''

    name = models.CharField(max_length=50, unique=True)
    permissions = models.ManyToManyField('Permission', blank=True, null=True)
    modules = models.ForeignKey(Client, blank=True, null=True)

    def __unicode__(self):
        return self.name
