#! /usr/bin/python
# -*- coding: utf-8 -*-

from django.contrib import admin
from apps.permissions.models import Role, Permission


@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    fields = ('name', 'modules', 'permissions', )


@admin.register(Permission)
class PermissionAdmin(admin.ModelAdmin):
    fields = ('action_type', 'target_type', 'target_id',)
