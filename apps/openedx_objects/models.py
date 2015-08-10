from django.db import models
from django.conf import settings


class BaseObjectModel(models.Model):
    is_published = models.BooleanField(default=True)
    is_archived = models.BooleanField(default=False)

    class Meta:
        abstract = True


class EdxOrg(BaseObjectModel):
    name = models.CharField(max_length=128, unique=True)

    def __unicode__(self):
        return self.name


class EdxCourse(BaseObjectModel):
    name = models.CharField(max_length=128, unique=True)
    course_id = models.CharField(max_length=255, unique=True)
    start = models.DateTimeField()
    end = models.DateTimeField(null=True)
    org = models.ForeignKey(EdxOrg)

    def __unicode__(self):
        return self.name or self.course_id


class EdxCourseRun(BaseObjectModel):
    name = models.CharField(max_length=128)
    course = models.ForeignKey(EdxCourse)

    class Meta:
        unique_together = (('name', 'course'),)

    def __unicode__(self):
        return self.name


class EdxCourseEnrollment(BaseObjectModel):
    name = models.CharField(max_length=128, blank=True)
    mode = models.CharField(default="honor", max_length=100)
    is_active = models.BooleanField(default=True)
    course = models.ForeignKey(EdxCourse)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, null=True)

    class Meta:
        unique_together = (('user', 'course'),)

    def __unicode__(self):
        return U'%s enrollment of course %s' % (self.user, self.course)
