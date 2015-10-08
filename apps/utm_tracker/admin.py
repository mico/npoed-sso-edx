from django.contrib import admin
from apps.utm_tracker.models import UTMUserTags


@admin.register(UTMUserTags)
class UTMUserTagsAdmin(admin.ModelAdmin):
    list_display = ['user', 'utm_source', 'utm_medium', 'utm_term', 'utm_content', 'utm_campaign']
