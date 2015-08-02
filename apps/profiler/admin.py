from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin


@admin.register(get_user_model())
class CustomUserAdmin(UserAdmin):
    # fieldsets = UserAdmin.fieldsets + ((None, {
    #             'fields': ('buisness', 'gender', 'subscribe', 'date_of_birth',
    #                        'team_or_idol', 'team_for_idol',
    #                        'icon_profile', 'curent_photo', 'user_members',
    #                        'country', 'city', 'post_code', )}, ), )
    fieldsets = UserAdmin.fieldsets + ((None, {
                'fields': ('date_of_birth', )}, ), )
