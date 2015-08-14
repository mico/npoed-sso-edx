from django.contrib import admin

from .models import EdxCourse, EdxOrg, EdxCourseRun, EdxCourseEnrollment


class EdxOrgAdmin(admin.ModelAdmin):
    pass


class EdxCourseAdmin(admin.ModelAdmin):
    list_display = ['name', 'course_id', 'org', 'start',
                     'is_published', 'is_archived']


class EdxCourseRunAdmin(admin.ModelAdmin):
    list_display = ['name', 'course', 'is_published', 'is_archived']


class EdxCourseEnrollmentAdmin(admin.ModelAdmin):
    list_display = ['user', 'course', 'mode', 'is_active',
                    'is_published', 'is_archived']


admin.site.register(EdxOrg, EdxOrgAdmin)
admin.site.register(EdxCourse, EdxCourseAdmin)
admin.site.register(EdxCourseRun, EdxCourseRunAdmin)
admin.site.register(EdxCourseEnrollment, EdxCourseEnrollmentAdmin)
