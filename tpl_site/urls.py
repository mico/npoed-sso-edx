from django.conf.urls import patterns, include, url
from django.contrib import admin
from django.contrib.auth.views import login, logout
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt

from apps.core.views import AccessTokenDetailView
from apps.core.decorators import set_auth_cookie, external_redirect


urlpatterns = patterns(
    '', 
    url(r'^$', include('apps.core.urls')),
    url(r'^login/', set_auth_cookie(login), name='login'),
    url(r'^logout/', external_redirect(set_auth_cookie(logout)),
        {'next_page': '/'}, name='logout'),
    url(r'^admin/', include(admin.site.urls)),
    url('^oauth2/access_token/(?P<token>[\w]+)/$',
        csrf_exempt(AccessTokenDetailView.as_view()),
        name='access_token_detail'),
    url(r'^oauth2/', include('oauth2_provider.urls', namespace = 'oauth2')),
)

if settings.DEBUG:
    urlpatterns += patterns(
        '', url(r'^media/(?P<path>.*)$', 'django.views.static.serve', {
                'document_root': settings.MEDIA_ROOT, }),
        )
    from django.contrib.staticfiles.urls import staticfiles_urlpatterns
    urlpatterns += staticfiles_urlpatterns()
