# coding: utf-8
from django.conf import settings
from django.conf.urls import patterns, include, url
from django.contrib.admin import site as admin_site
from django.contrib.auth.views import logout
from django.views.generic import TemplateView
from django.views.generic.base import RedirectView
from django.contrib.auth.decorators import login_required

from social.apps.django_app.views import complete
from social.utils import setting_name
from functools import update_wrapper
from oauth2_provider.views import Redirect

from apps.core.decorators import set_auth_cookie, external_redirect
from apps.core.views import login
from apps.profiler.views import (
    CustomActivationView, Login, RegistrationView, UserProfileAPI,
    RegisteredView, email_complete, IncorrectKeyView
)
from apps.profiler.forms import (
    CustomPasswordResetForm, CustomSetPasswordForm, CustomPasswordChangeForm
)

extra = getattr(settings, setting_name('TRAILING_SLASH'), True) and '/' or ''


def wrap_admin(view, cacheable=False):
    def wrapper(*args, **kwargs):
        return admin_site.admin_view(view, cacheable)(*args, **kwargs)
    wrapper.admin_site = admin_site
    return update_wrapper(wrapper, view)


urlpatterns = patterns(
    '',
    url(r'^favicon\.ico$', RedirectView.as_view(url='/static/images/favicon.ico')),
    #  админка
    url(r'^admin/login/$', set_auth_cookie(admin_site.login), name='admin:login'),
    url(r'^admin/logout/$', set_auth_cookie(wrap_admin(admin_site.logout)), name='logout'),
    url(r'^admin/', include(admin_site.urls)),

    # social auth
    url(r'^email_complete/(?P<backend>[^/]+){0}$'.format(extra),
        set_auth_cookie(email_complete), name='email_complete'),
    url(r'^complete/(?P<backend>[^/]+){0}$'.format(extra),
        set_auth_cookie(complete), name='social:complete'),
    url(r'^', include('social.apps.django_app.urls', namespace='social')),

    url(r'^', include('apps.profiler.urls')),
    url(r'^', include('apps.core.urls')),

    url(r'^accounts/activate/(?P<activation_key>\w+)/$',
        set_auth_cookie(CustomActivationView.as_view()),
        name='registration_activate'),
    url(r'^register/$', set_auth_cookie(RegistrationView.as_view()),
        name='registration_register2'),
    url(r'^accounts/', include('registration.backends.default.urls')),
    # подтвержения регистрации
    url(r'^registered/$', set_auth_cookie(RegisteredView.as_view()),
        name='registered'),

    # логин
    url(r'^login/', set_auth_cookie(login), name='login'),
    url(r'^logout/', external_redirect(set_auth_cookie(logout)),
        {'next_page': '/'}, name='logout'),

    #  смена пароля
    url(r'^accounts/password_change/$',
        'django.contrib.auth.views.password_change',
        {'password_change_form': CustomPasswordChangeForm},
        name="password_change"),
    url(r'^accounts/password_changed/$',
        'django.contrib.auth.views.password_change_done',
        name="password_change_done"),

    #  сброс пароля
    url(r'^user/password/reset/$',
        'django.contrib.auth.views.password_reset',
        {'post_reset_redirect': '/user/password/reset/done/',
         'password_reset_form': CustomPasswordResetForm},
        name="password_reset"),
    (r'^user/password/reset/done/$',
        'django.contrib.auth.views.password_reset_done'),
    (r'^user/password/reset/(?P<uidb64>[0-9A-Za-z]+)-(?P<token>.+)/$',
        'django.contrib.auth.views.password_reset_confirm',
        {'post_reset_redirect': '/user/password/done/',
         'set_password_form': CustomSetPasswordForm}),
    (r'^user/password/done/$',
        'django.contrib.auth.views.password_reset_complete'),


    url(r'^email-sent/$', 'apps.profiler.views.validation_sent'),
    url(r'^ajax-auth/(?P<backend>[^/]+)/$', 'apps.profiler.views.ajax_auth',
        name='ajax-auth'),
    url(r'^email/$', 'apps.profiler.views.require_email', name='require_email'),
    url(r'^email-change/$', 'apps.profiler.views.email_change', name='email_change'),
    url(r'^incorrect-activation-key/$', IncorrectKeyView.as_view(), name='incorrect_key'),

    url('^oauth2/redirect/?$',
        set_auth_cookie(login_required(Redirect.as_view())), name='redirect'),
    url(r'^oauth2/', include('oauth2_provider.urls', namespace='oauth2')),

    # url(r'^done/$', 'apps.profiler.views.done', name='done'),
    # url(r'^/receiver.html$',
    #     TemplateView.as_view(template_name='-receiver.html')),

    #  API
    url(r'^', include('apps.openedx_objects.urls', namespace='api-edx')),
    url(r'^', include('apps.permissions.urls', namespace='api-permissions'))
)


if settings.DEBUG:
    urlpatterns += patterns(
        '', url(r'^media/(?P<path>.*)$', 'django.views.static.serve', {
                'document_root': settings.MEDIA_ROOT, }),
        )
    from django.contrib.staticfiles.urls import staticfiles_urlpatterns
    urlpatterns += staticfiles_urlpatterns()
