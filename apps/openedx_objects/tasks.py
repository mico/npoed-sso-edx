from django.conf import settings
from django.core.urlresolvers import reverse

from .models import EdxCourse, EdxOrg, EdxCourseRun, EdxCourseEnrollment
from .utils import datetime_parser
from apps.profiler.models import User

import requests
import json


_uoc_course = EdxCourse.objects.update_or_create
_uoc_org = EdxOrg.objects.update_or_create
_uoc_run = EdxCourseRun.objects.update_or_create
_uoc_enrollment = EdxCourseEnrollment.objects.update_or_create
_SESSION = requests.Session()


def get_edx_objects():
    is_login = login()
    if not is_login:
        print 'Log in error'
        return None

    url = settings.EDX_COURSES_API
    params = {'format': 'json'}
    enrl_params = params
    courses = []
    enrollments = []
    orgs = []
    runs = []

    while True:
        r = _SESSION.get(url, params=params)
        data = json.loads(r.text, object_hook=datetime_parser)

        for course in data.get('results', []):
            if course['org'] not in orgs:
                org_obj, created = _uoc_org(name=course['org'])
                org_obj.id not in orgs and orgs.append(org_obj.id)
                if created:
                    print 'Organisation "%s" is created' % course['org']

            course_id = course.pop('id')
            course_obj, created = _uoc_course(
                course_id=course_id,
                defaults={
                    'name': course['name'],
                    'start': course['start'],
                    'end': course['end'],
                    'org': org_obj
                }
            )

            if created:
                print 'Course "%s" is created' % course['name']

            if course_obj.id not in courses:
                courses.append(course_obj.id)

            run_obj, run_created = _uoc_run(name=course['run'], course=course_obj)

            if run_created:
                print 'Course run "%s" is created' % course['run']

            if run_obj.id not in runs:
                runs.append(run_obj.id)
                enrl_params['course_run'] = course_id
                r = _SESSION.get(settings.EDX_ENROLLMENTS_API, params=enrl_params)
                result = json.loads(r.text, object_hook=datetime_parser)
                enrollments.extend(add_enrollments(result, run_obj))

        url = data.get('next')
        if url is None:
            break

    EdxCourseEnrollment.objects.exclude(id__in=enrollments).delete()
    EdxCourseRun.objects.exclude(id__in=runs).delete()
    EdxCourse.objects.exclude(id__in=courses).delete()
    EdxOrg.objects.exclude(id__in=orgs).delete()


def add_enrollments(result, run_obj):
    enrollments = []
    for enrollment in result:
        try:
            user = User.objects.get(username=enrollment['user'])
        except User.DoesNotExist:
            continue
        else:
            enrollment_obj, created = _uoc_enrollment(
                user=user,
                course_run=run_obj,
                defaults={
                    'mode': enrollment['mode'],
                    'is_active': enrollment['is_active'],
                }
            )
            enrollments.append(enrollment_obj.id)
            if created:
                print 'Enrollment "%s - %s" is created' % (enrollment['user'],
                                                            run_obj)

    return enrollments


def login():
    r = _SESSION.get(settings.EDX_API_LOGIN_URL,
                     params={'auth_entry': 'login', 'next': '/'})

    post_login_data = {
        'username': settings.EDX_API_USER,
        'password': settings.EDX_API_PASS,
        'csrfmiddlewaretoken': r.cookies.get('csrftoken'),
    }

    login_url = reverse('login')
    domain = '/'.join(r.url.split('/')[:3])
    querystring = '?'.join(r.url.split('?')[1:])
    full_login_url = '%s%s?%s' % (domain, login_url, querystring)
    cookies = r.cookies
    r = _SESSION.post(full_login_url, data=post_login_data)
    if not r.ok or domain in r.url:
        return False

    return True