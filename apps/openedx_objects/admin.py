from django.contrib import admin

from .models import EdxCourse, EdxOrg, EdxCourseRun, EdxCourseEnrollment


class EdxOrgAdmin(admin.ModelAdmin):
    pass


class EdxCourseAdmin(admin.ModelAdmin):
    pass


class EdxCourseRunAdmin(admin.ModelAdmin):
    pass


class EdxCourseEnrollmentAdmin(admin.ModelAdmin):
    pass


admin.site.register(EdxOrg, EdxOrgAdmin)
admin.site.register(EdxCourse, EdxCourseAdmin)
admin.site.register(EdxCourseRun, EdxCourseRunAdmin)
admin.site.register(EdxCourseEnrollment, EdxCourseEnrollmentAdmin)
