from django.contrib import admin

from .models import EdxCourse, EdxOrg, EdxCourseRun, EdxCourseEnrollment


class EdxCourseEnrollmentAdmin(admin.ModelAdmin):
    list_display = ['user', 'course_run', 'mode', 'is_active',
                    'is_published', 'is_archived']


class EdxCourseEnrollInline(admin.TabularInline):
    model = EdxCourseEnrollment


class EdxCourseRunAdmin(admin.ModelAdmin):
    list_display = ['name', 'course', 'is_published', 'is_archived']
    inlines = [EdxCourseEnrollInline, ]


class EdxCourseRunInline(admin.TabularInline):
    model = EdxCourseRun


class EdxCourseAdmin(admin.ModelAdmin):
    list_display = ['name', 'course_id', 'org', 'start',
                     'is_published', 'is_archived']
    inlines = [EdxCourseRunInline, ]


class EdxCourseInline(admin.TabularInline):
    model = EdxCourse


class EdxOrgAdmin(admin.ModelAdmin):
    inlines = [EdxCourseInline, ]


admin.site.register(EdxOrg, EdxOrgAdmin)
admin.site.register(EdxCourse, EdxCourseAdmin)
admin.site.register(EdxCourseRun, EdxCourseRunAdmin)
admin.site.register(EdxCourseEnrollment, EdxCourseEnrollmentAdmin)
