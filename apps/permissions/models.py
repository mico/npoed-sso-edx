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


class Action(models.Model):
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
    )
    obj_choices = (
        ('Org', 'Org', ),
        ('Course', 'Course', ),
        ('CourseRun', 'CourseRun', ),
        ('Profile', 'Profile', ),
        ('Progress', 'Progress', ),
        ('Data', 'Data', ),
        ('VideoFragment', 'VideoFragment', ),
    )

    action_type = models.CharField(
        max_length=50, choices=action_choices, blank=True, null=True
    )
    target_type = models.CharField(
        max_length=50, choices=obj_choices, blank=True, null=True
    )
    target_id = models.PositiveIntegerField(
        blank=True, null=True
    )

    def __unicode__(self):
        return self.action_type


class Role(models.Model):
    '''
    Model of roles for sharing permissions to sso.
    '''

    name = models.CharField(max_length=50)
    actions = models.ManyToManyField('Action', blank=True, null=True)
    modules = models.CharField(max_length=50, blank=True, null=True)

    def __unicode__(self):
        return self.name
