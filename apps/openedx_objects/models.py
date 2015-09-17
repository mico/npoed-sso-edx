#! /usr/bin/python
# -*- coding: utf-8 -*-

from django.db import models
from django.conf import settings


class BaseObjectModel(models.Model):
    """
    Базовая абстрактная модель для объектов из edx
    """
    is_published = models.BooleanField(default=True)
    is_archived = models.BooleanField(default=False)

    class Meta:
        abstract = True


class EdxOrg(BaseObjectModel):
    """
    Модель для хранения объектов организации создавших курс в edx
    """
    name = models.CharField(max_length=128, unique=True)

    class Meta:
        verbose_name = 'edxorg'

    def __unicode__(self):
        return self.name


class EdxCourse(BaseObjectModel):
    """
    Модель для хранения объектов курса в edx
    """

    name = models.CharField(max_length=128)
    course_id = models.CharField(max_length=255, unique=True)
    start = models.DateTimeField()
    end = models.DateTimeField(null=True)
    org = models.ForeignKey(EdxOrg)

    class Meta:
        verbose_name = 'edxcourse'

    def __unicode__(self):
        return self.name or self.course_id


class EdxLibrary(BaseObjectModel):
    """
    Модель для хранения объектов библиотек в edx
    """

    course_id = models.CharField(max_length=255, unique=True)
    org = models.ForeignKey(EdxOrg)

    class Meta:
        verbose_name = 'edxlibrary'

    def __unicode__(self):
        return self.course_id


class EdxCourseRun(BaseObjectModel):
    """
    Модель для хранения объектов конкретного запуска курса в edx
    """

    name = models.CharField(max_length=128)
    course = models.ForeignKey(EdxCourse)

    class Meta:
        unique_together = (('name', 'course'),)
        verbose_name = 'edxcourserun'

    def __unicode__(self):
        return self.name


class EdxCourseEnrollment(BaseObjectModel):
    """
    Модель для хранения записей об участии пользователей в конкретном запуске курса в edx
    """

    name = models.CharField(max_length=128, blank=True)
    mode = models.CharField(default="honor", max_length=100)
    is_active = models.BooleanField(default=True)
    course_run = models.ForeignKey(EdxCourseRun)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, null=True)

    class Meta:
        unique_together = (('user', 'course_run'),)
        verbose_name = 'edxcourseenrollment'

    def __unicode__(self):
        return U'%s enrollment of course %s' % (self.user, self.course_run)
