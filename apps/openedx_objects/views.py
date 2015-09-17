#! /usr/bin/python
# -*- coding: utf-8 -*-
"""
API для доступа к отображению edx объектов в sso
Нужны для инкрементальных апдейтов, чтоб edx мог присылать в sso новые и
редактировать старые объекты курсов и енролментов
"""
from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model
from django.http import HttpResponse, JsonResponse
from django.contrib.contenttypes.models import ContentType
from django.dispatch import receiver
from django.db.models import Q

from rest_framework.decorators import api_view
from provider.oauth2.models import Grant, Client

from apps.profiler.models import User
from .models import EdxCourse, EdxOrg, EdxCourseRun, EdxCourseEnrollment
from .signals import api_course_create

import json
import string
import random
import requests

User = get_user_model()


@api_view(['POST'])
def course(request):
    message = 'Course is updated!'
    data = request.data.dict()
    run_name = data.pop('run', None)
    org_name = data.pop('org', None)
    course_id = data.pop('course_id', None)

    org_obj, org_created = EdxOrg.objects.update_or_create(name=org_name)
    data['org'] = org_obj

    course_obj, course_created = EdxCourse.objects.update_or_create(course_id=course_id,
                                                                defaults=data)

    run_obj, run_created = EdxCourseRun.objects.update_or_create(name=run_name,
                                                             course=course_obj)

    if course_created:
        if not org_created:
            api_course_create.send(course, obj=course_obj, request=request)
        message = 'Course is created!'
    elif run_created:
        api_course_create.send(course, obj=run_obj, request=request)

    return HttpResponse(json.dumps({'message': message, 'status': 'SUCCESS'}),
                        content_type="application/json")


@api_view(['POST'])
def library(request):
    message = 'Library is updated!'
    data = request.data.dict()
    org_name = data.pop('org', None)
    course_id = data.pop('course_id', None)

    org_obj, org_created = EdxOrg.objects.update_or_create(name=org_name)
    data['org'] = org_obj

    course_obj, course_created = EdxLibrary.objects.update_or_create(
        course_id=course_id, defaults=data)
    if course_created:
        if not org_created:
            api_course_create.send(library, obj=course_obj, request=request)
        message = 'Library is created!'

    return JsonResponse({'message': message, 'status': 'SUCCESS'})


@api_view(['POST', 'DELETE'])
def enrollment(request):
    data = request.data.dict()
    if request.method == 'POST':
        message = 'Course enrollment is updated!'
        username = data.pop('user')
        course_id = data.pop('course_id')
        course_run = data.pop('course_run')
        data['is_active'] = (data['is_active'] == 'True')
        user = get_object_or_404(User, username=username)
        course_run = get_object_or_404(EdxCourseRun,
                                       course__course_id=course_id,
                                       name=course_run)
        enrollment, created = EdxCourseEnrollment.objects.update_or_create(
            user=user,
            course_run=course_run,
            defaults=data
        )
        if created:
            message = 'Course enrollment is created!'
        return HttpResponse(json.dumps({'message': message, 'status': 'SUCCESS'}),
                        content_type="application/json")

    elif request.method == 'DELETE':
        username = data.get('user')
        course_id = data.get('course_id')
        course_run = data.pop('course_run')

        EdxCourseEnrollment.objects.filter(user__username=username,
                            course_run__name=course_run,
                            course_run__course__course_id=course_id).delete()
        return HttpResponse(json.dumps({'message': 'CourseEnrollment is deleted',
                         'status': 'SUCCESS'}), content_type="application/json")


@receiver(api_course_create)
def _update_course_permissions(sender, obj, request, **kwargs):
    """
    Обработчик сигнала. При создании нового курса, происходит синхронизация ролей пользователей
    из sso в edx, которые имеют права более высого уровня по иерархии к данному курсу
    """
    org_content_type = ContentType.objects.get_for_model(EdxOrg)
    course_content_type = ContentType.objects.get_for_model(EdxCourse)

    if isinstance(obj, EdxCourse):
        users = User.objects.prefetch_related().filter(
            role__permissions__target_id=obj.org_id,
            role__permissions__target_type=org_content_type
        ).distinct()
    else:
        users = User.objects.prefetch_related().filter(
            Q(
                role__permissions__target_id=obj.course.org_id,
                role__permissions__target_type=org_content_type
            )|
            Q(
                role__permissions__target_id=obj.course_id,
                role__permissions__target_type=course_content_type
            )
        ).distinct()
    _update_roles(users, request)


def _update_roles(users, request):
    client = Client.objects.filter(url__contains=request.META['REMOTE_HOST'])

    for user in users.iterator():
        role = user.role.first()
        if client:
            grant = Grant.objects.create(
                user=user,
                client=client[0],
                redirect_uri=client[0].redirect_uri,
                scope=2
            )

            params = urllib.urlencode({
                'state': ''.join(random.sample(string.ascii_letters, 32)),
                'code': grant.code
            })

            r = requests.get('%s?%s' % (url, params, ))
