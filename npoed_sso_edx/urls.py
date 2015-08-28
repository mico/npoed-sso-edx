from django.conf import settings
from django.conf.urls import patterns, include, url
from django.contrib.admin import site as admin_site
from django.contrib.auth.views import logout
from django.views.generic import TemplateView

from social.utils import setting_name
from social.apps.django_app.views import complete

from apps.core.decorators import set_auth_cookie, external_redirect
from apps.core.views import login
from apps.profiler.views import (
    CustomActivationView, Login, RegistrationView, Profile
)

from social.utils import setting_name
from functools import update_wrapper



extra = getattr(settings, setting_name('TRAILING_SLASH'), True) and '/' or ''


def wrap_admin(view, cacheable=False):
    def wrapper(*args, **kwargs):
        return admin_site.admin_view(view, cacheable)(*args, **kwargs)
    wrapper.admin_site = admin_site
    return update_wrapper(wrapper, view)


urlpatterns = patterns(
    '',
    url(r'^admin/login/$', set_auth_cookie(admin_site.login), name='admin:login'),
    url(r'^admin/logout/$', set_auth_cookie(wrap_admin(admin_site.logout)), name='logout'),
    url(r'^admin/', include(admin_site.urls)),

    url(r'^', include('apps.core.urls')),
    url(r'^', include('apps.profiler.urls')),

    url(r'^complete/(?P<backend>[^/]+){0}$'.format(extra),
        set_auth_cookie(complete), name='social:complete'),
    url('', include('social.apps.django_app.urls', namespace='social')),

    url(r'^accounts/activate/(?P<activation_key>\w+)/$',
        set_auth_cookie(CustomActivationView.as_view()),
        name='registration_activate'),
    url(r'^register/$', set_auth_cookie(RegistrationView.as_view()),
        name='registration_register2'),

    url(r'^accounts/', include('registration.backends.default.urls')),

    url(r'^user/password/reset/$',
        'django.contrib.auth.views.password_reset',
        {'post_reset_redirect': '/user/password/reset/done/'},
        name="password_reset"),
    (r'^user/password/reset/done/$',
        'django.contrib.auth.views.password_reset_done'),
    (r'^user/password/reset/(?P<uidb64>[0-9A-Za-z]+)-(?P<token>.+)/$',
        'django.contrib.auth.views.password_reset_confirm',
        {'post_reset_redirect': '/user/password/done/'}),
    (r'^user/password/done/$',
        'django.contrib.auth.views.password_reset_complete'),

    # url(r'^accounts/password/reset/(?P<uidb64>[0-9A-Za-z]+)-(?P<token>.+)/$',
    #     'django.contrib.auth.views.password_reset_confirm',
    #     {'post_reset_redirect' : '/accounts/password/done/'}),
    url(r'^accounts/reset/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$',
        'django.contrib.auth.views.password_reset_confirm',
        name='password_reset_confirm'),
    url(r'^accounts/reset/complete/$',
        'django.contrib.auth.views.password_reset_complete',
        name='password_reset_complete'),
    url('^accounts/password_change/',
        'django.contrib.auth.views.password_change',
        name="password_change"),
    url(r'^accounts/password_changed/$',
        'django.contrib.auth.views.password_change_done',
        name="password_change_done"),

    url(r'^email-sent/', 'apps.profiler.views.validation_sent'),
    url(r'^done/$', 'apps.profiler.views.done', name='done'),
    url(r'^ajax-auth/(?P<backend>[^/]+)/$', 'apps.profiler.views.ajax_auth',
        name='ajax-auth'),
    url(r'^email/$', 'apps.profiler.views.require_email', name='require_email'),


    url(r'^login/', set_auth_cookie(login), name='login'),
    url(r'^login_auth/$', set_auth_cookie(Login.as_view()), name='login_auth'),
    url(r'^logout/', external_redirect(set_auth_cookie(logout)),
        {'next_page': '/'}, name='logout'),
    url(r'profile/$', Profile.as_view(), name='profile'),

    url(r'^oauth2/', include('oauth2_provider.urls', namespace = 'oauth2')),
    url(r'^/receiver.html$',
        TemplateView.as_view(template_name='-receiver.html')
    ),
    url(r'^login-form/$',
        TemplateView.as_view(template_name='login_form.html'), name='login_form'
    ),
    url(r'', include('apps.openedx_objects.urls', namespace='api-edx')),
    url(r'', include('apps.permissions.urls', namespace='api-permissions'))
)


if settings.DEBUG:
    urlpatterns += patterns(
        '', url(r'^media/(?P<path>.*)$', 'django.views.static.serve', {
                'document_root': settings.MEDIA_ROOT, }),
        )
    from django.contrib.staticfiles.urls import staticfiles_urlpatterns
    urlpatterns += staticfiles_urlpatterns()
