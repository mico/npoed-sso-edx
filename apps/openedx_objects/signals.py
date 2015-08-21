import django.dispatch
 
 
api_course_create = django.dispatch.Signal(providing_args=['course', 'request'])
