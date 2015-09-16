from django.conf.urls import url, patterns
from apps.openedx_objects import views


urlpatterns = patterns('',
    url(r'^api-edx/enrollment/$', views.enrollment, name='enrollment'),
    url(r'^api-edx/course/$', views.course, name='course'),
)
