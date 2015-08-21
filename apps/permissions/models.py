#! /usr/bin/python
# -*- coding: utf-8 -*-
"""
    apps.permissions.models
    ~~~~~~~~~

    :copyright: (c) 2015 by dorosh.
"""

__author__ = 'dorosh'
__date__ = '07.08.2015'

from django.db import models
from django.contrib.contenttypes.models import ContentType

from provider.oauth2.models import Client


class Permission(models.Model):
    '''
    Model of actions for objects from another modules.
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

    def get_object(self):
        return self.target_type.model_class().objects.get(pk=self.target_id)


class Role(models.Model):
    '''
    Model of roles for sharing permissions to sso.
    '''

    name = models.CharField(max_length=50)
    permissions = models.ManyToManyField('Permission', blank=True, null=True)
    modules = models.ForeignKey(Client, blank=True, null=True)

    def __unicode__(self):
        return self.name
