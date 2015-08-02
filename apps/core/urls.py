from django.conf.urls import patterns, include, url
from apps.core.views import Home, Index


urlpatterns = patterns(
    '', url(r'^$', Index.as_view(), name='index'),
    url(r'^home/$', Home.as_view(), name='home'),
)
