import django.dispatch
 
 
api_course_create = django.dispatch.Signal(providing_args=['obj', 'request'])
