from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model
from django.http import HttpResponse
from django.contrib.contenttypes.models import ContentType
from django.dispatch import receiver
from django.db.models import Q

from rest_framework.decorators import api_view
from provider.oauth2.models import Grant, Client

from apps.profiler.models import User
from .models import EdxCourse, EdxOrg
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
            api_course_create.send(course_obj, request)
        message = 'Course is created!'
    elif run_created:
        api_course_create.send(run_obj, request)

    return HttpResponse(json.dumps({'message': message, 'status': 'SUCCESS'}),
                        content_type="application/json")


@api_view(['POST', 'DELETE'])
def enrollment(request):
    data = request.data.dict()
    if request.method == 'POST':
        message = 'Course enrollment is updated!'
        username = data.pop('user')
        course_id = data.pop('course_id')
        data['is_active'] = (data['is_active'] == 'True')
        user = get_object_or_404(User, username=username)
        course = get_object_or_404(EdxCourse, course_id=course_id)
        enrollment, created = EdxCourseEnrollment.objects.update_or_create(
            user=user,
            course=course,
            defaults=data
        )
        if created:
            message = 'Course enrollment is created!'
        return HttpResponse(json.dumps({'message': message, 'status': 'SUCCESS'}),
                        content_type="application/json")

    elif request.method == 'DELETE':
        username = data.get('user')
        course_id = data.get('course_id')

        EdxCourseEnrollment.objects.filter(user__username=username,
                                           course__course_id=course_id).delete()
        return HttpResponse(json.dumps({'message': 'CourseEnrollment is deleted',
                         'status': 'SUCCESS'}), content_type="application/json")


@receiver(api_course_create)
def _update_course_permissions(sender, obj, request **kwargs):
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
