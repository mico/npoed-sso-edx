from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model
from django.http import HttpResponse

from rest_framework.decorators import api_view

from .models import EdxCourse, EdxCourseRun, EdxOrg, EdxCourseEnrollment

import json

User = get_user_model()


@api_view(['POST'])
def course(request):
    message = 'Course is updated!'
    data = request.data.dict()
    run_name = data.pop('run', None)
    org_name = data.pop('org', None)
    course_id = data.pop('course_id', None)

    org, org_created = EdxOrg.objects.update_or_create(name=org_name)
    data['org'] = org

    course, course_created = EdxCourse.objects.update_or_create(course_id=course_id,
                                                                defaults=data)

    run, run_created = EdxCourseRun.objects.update_or_create(name=run_name,
                                                             course=course)

    if course_created:
        message = 'Course is created!'

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
