from django.contrib import admin

from .models import (
    EdxCourse, EdxOrg, EdxCourseRun, EdxCourseEnrollment, EdxLibrary
)


class EdxCourseEnrollmentAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'course_run', 'mode', 'is_active',
                    'is_published', 'is_archived']


class EdxCourseEnrollInline(admin.TabularInline):
    model = EdxCourseEnrollment


class EdxCourseRunAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'course', 'is_published', 'is_archived']
    inlines = [EdxCourseEnrollInline, ]


class EdxCourseRunInline(admin.TabularInline):
    model = EdxCourseRun


class EdxCourseAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'course_id', 'org', 'start',
                    'is_published', 'is_archived']
    inlines = [EdxCourseRunInline, ]


class EdxCourseInline(admin.TabularInline):
    model = EdxCourse


class EdxOrgAdmin(admin.ModelAdmin):
    inlines = [EdxCourseInline, ]


class EdxLibraryAdmin(admin.ModelAdmin):
    list_display = ['id', 'course_id', 'org', 'is_published', 'is_archived']


admin.site.register(EdxLibrary, EdxLibraryAdmin)
admin.site.register(EdxOrg, EdxOrgAdmin)
admin.site.register(EdxCourse, EdxCourseAdmin)
admin.site.register(EdxCourseRun, EdxCourseRunAdmin)
admin.site.register(EdxCourseEnrollment, EdxCourseEnrollmentAdmin)
