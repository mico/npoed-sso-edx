from django.conf import settings
from django.core.urlresolvers import reverse

from .models import EdxCourse, EdxOrg, EdxCourseRun, EdxCourseEnrollment
from apps.profiler.models import User

import requests
import json
import re


_uoc_course = EdxCourse.objects.update_or_create
_uoc_org = EdxOrg.objects.update_or_create
_uoc_run = EdxCourseRun.objects.update_or_create
_uoc_enrollment = EdxCourseEnrollment.objects.update_or_create


def get_edx_objects():
    r = login()
    url = settings.EDX_COURSES_API
    params = {'format': 'json'}
    enrl_params = params
    courses = []
    enrollments = []
    orgs = []
    runs = []

    while True:
        r.cookies['authenticated'] = '1'
        r = requests.get(url, cookies=r.cookies, params=params)
        data = json.loads(r.text, object_hook=_datetime_parser)

        for course in data.get('results', []):
            if course['org'] not in orgs:
                org_obj, created = _uoc_org(name=course['org'])
                org_obj.id not in orgs and orgs.append(org_obj.id)
                if created:
                    print 'Organisation "%s" is created' % course['org']

            course_obj, created = _uoc_course(
                course_id=course['id'],
                name=course['name'],
                start=course['start'],
                org=org_obj
            )

            if created:
                print 'Course "%s" is created' % course['name']

            if course_obj.id not in courses:
                courses.append(course_obj.id)
                enrl_params['course'] = course['id']
                r.cookies['authenticated'] = '1'
                r = requests.get(settings.EDX_ENROLLMENTS_API,
                                 cookies=r.cookies, params=enrl_params)
                result = json.loads(r.text, object_hook=_datetime_parser)
                enrollments.extend(add_enrollments(result, course_obj))

            run_obj, created = _uoc_run(name=course['run'], course=course_obj)
            run_obj.id not in runs and runs.append(run_obj.id)
            if created:
                print 'Course run "%s" is created' % course['run']

        url = data.get('next')
        if url is None:
            break

    EdxCourseEnrollment.objects.exclude(id__in=enrollments).delete()
    EdxCourseRun.objects.exclude(id__in=runs).delete()
    EdxCourse.objects.exclude(id__in=courses).delete()
    EdxOrg.objects.exclude(id__in=orgs).delete()


def add_enrollments(result, course_obj):
    enrollments = []
    for enrollment in result:
        try:
            user = User.objects.get(username=enrollment['user'])
        except User.DoesNotExist:
            continue
        else:
            enrollment_obj, created = _uoc_enrollment(
                user=user,
                mode=enrollment['mode'],
                is_active=enrollment['is_active'],
                course=course_obj
            )
            enrollments.append(enrollment_obj.id)
            if created:
                print 'Enrollment "%s - %s" is created' % (enrollment['user'],
                                                            course_obj)

    return enrollments


def login():
    r = requests.get(settings.EDX_API_LOGIN_URL,
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
    r = requests.post(full_login_url, data=post_login_data, cookies=cookies)
    if r.ok and domain not in r.url:
        r.cookies['authenticated'] = '1'
        return r

    print 'Log in error'
    exit()

def _datetime_parser(dct):
    for k, v in dct.items():
        if (isinstance(v, basestring)
            and re.search("\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z", v)):
            try:
                dct[k] = datetime.datetime.strptime(v, '%Y-%m-%dT%H:%M:%SZ')
            except ValueError:
                pass
    return dct
