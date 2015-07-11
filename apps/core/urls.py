from django.conf.urls import patterns, include, url
from apps.core.views import Home


urlpatterns = patterns(
    '', url(r'^$', Home.as_view(), name='home'),
)
