#! /usr/bin/python
# -*- coding: utf-8 -*-
"""
    apps.permissions.admin
    ~~~~~~~~~

    :copyright: (c) 2015 by dorosh.
"""

__author__ = 'dorosh'
__date__ = '07.08.2015'

from django.contrib import admin
from apps.permissions.models import Role, Permission


@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    fields = ('name', 'modules', 'permissions', )


@admin.register(Permission)
class PermissionAdmin(admin.ModelAdmin):
    fields = ('action_type', 'target_type', 'target_id',)
