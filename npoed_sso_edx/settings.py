"""
Django settings for npoed_sso_edx project.

For more information on this file, see
https://docs.djangoproject.com/en/1.7/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.7/ref/settings/
"""

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os
BASE_DIR = os.path.dirname(os.path.dirname(__file__))

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.7/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'kt#^esw))8@$i_=pk35t0fno5&04%1++s+iukj203#j8t-g=nw'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

TEMPLATE_DEBUG = True

AUTH_SESSION_COOKIE_DOMAIN = ".rnoep.raccoongang.com"

AUTH_USER_MODEL = 'profiler.User'

ALLOWED_HOSTS = ['*']

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework.authentication.TokenAuthentication',
        'rest_framework_oauth.authentication.OAuth2Authentication'
    ),
    'DEFAULT_PERMISSION_CLASSES': ('rest_framework.permissions.IsAdminUser',),
    'PAGE_SIZE': 10,
}

TEMPLATE_CONTEXT_PROCESSORS = (
    "django.contrib.auth.context_processors.auth",
    "django.core.context_processors.debug",
    "django.core.context_processors.i18n",
    "django.core.context_processors.media",
    "django.core.context_processors.static",
    "django.core.context_processors.tz",
    "django.contrib.messages.context_processors.messages",
    "django.core.context_processors.request",
    "apps.profiler.context_processors.forms",
)

INSTALLED_APPS = (
    # django apps
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.sites',
    'registration',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # utils apps
    'rest_framework',
    'rest_framework.authtoken',
    'provider',
    'provider.oauth2',
    'oauth2_provider',
    'gunicorn',
    'social.apps.django_app.default',
    'django_countries',
    # my apps
    'apps.core',
    'apps.profiler',
    'apps.permissions',
    'apps.openedx_objects',
)

RAVEN_CONFIG = None

OAUTH_OIDC_ISSUER = "https:///oauth2"

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'npoed_sso_edx.middleware.SocialAuthExceptionMiddleware',
)

ROOT_URLCONF = 'npoed_sso_edx.urls'

WSGI_APPLICATION = 'npoed_sso_edx.wsgi.application'

STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR,  "static_col")
STATICFILES_DIRS = (
    os.path.join(BASE_DIR, "static"),
    )

# Database
# https://docs.djangoproject.com/en/1.7/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}

# Internationalization
# https://docs.djangoproject.com/en/1.7/topics/i18n/

LANGUAGE_CODE = 'ru'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.7/howto/static-files/

STATIC_URL = '/static/'

TEMPLATE_DIRS = [os.path.join(BASE_DIR, 'templates')]

SOCIAL_AUTH_PIPELINE = (
    'social.pipeline.social_auth.social_details',
    'social.pipeline.social_auth.social_uid',
    'social.pipeline.social_auth.auth_allowed',
    'social.pipeline.social_auth.social_user',
    'social.pipeline.user.get_username',
    'apps.profiler.pipeline.require_email',
    'apps.profiler.pipeline.mail_validation',
    'social.pipeline.social_auth.associate_by_email',
    'social.pipeline.user.create_user',
    'social.pipeline.social_auth.associate_user',
    'social.pipeline.social_auth.load_extra_data',
    'social.pipeline.user.user_details',
    'apps.profiler.pipeline.update_profile',
)

AUTHENTICATION_BACKENDS = (
    'social.backends.facebook.FacebookOAuth2',
    'social.backends.google.GoogleOAuth2',
    'social.backends.twitter.TwitterOAuth',
    'social.backends.mailru.MailruOAuth2',
    'social.backends.vk.VKOAuth2',
    'social.backends.email.EmailAuth',
    'social.backends.username.UsernameAuth',
    'django.contrib.auth.backends.ModelBackend',
)

SOCIAL_AUTH_PROTECTED_USER_FIELDS = ['first_name', 'last_name']
SOCIAL_AUTH_FACEBOOK_SCOPE = ['email']
SOCIAL_AUTH_ADMIN_USER_SEARCH_FIELDS = ['username', 'first_name', 'last_name', 'email', 'gender', ]
SOCIAL_AUTH_FACEBOOK_PROFILE_EXTRA_PARAMS = {'fields': 'email,last_name,first_name,name,id'}
SOCIAL_AUTH_URL_NAMESPACE = 'social'
SOCIAL_AUTH_CREATE_USERS = True
SOCIAL_AUTH_SLUGIFY_USERNAMES = True
SOCIAL_AUTH_FORCE_RANDOM_USERNAME = False
SOCIAL_AUTH_DEFAULT_USERNAME = 'socialauth_user'
SOCIAL_AUTH_COMPLETE_URL_NAME = 'socialauth_complete'
SOCIAL_AUTH_ASSOCIATE_URL_NAME = 'socialauth_associate_complete'
SOCIAL_AUTH_ERROR_KEY = 'socialauth_error'
SOCIAL_AUTH_SLUGIFY_FUNCTION = 'apps.core.utils.slugify'

SOCIAL_AUTH_REDIRECT_IS_HTTPS = True
SOCIAL_AUTH_RAISE_EXCEPTIONS = False

SOCIAL_AUTH_ASSOCIATE_BY_EMAIL = True
SOCIAL_AUTH_FORCE_EMAIL_VALIDATION = True

SOCIAL_AUTH_GOOGLE_OAUTH_SCOPE = [
    'https://www.googleapis.com/auth/drive',
    'https://www.googleapis.com/auth/userinfo.profile'
]

SOCIAL_AUTH_EMAIL_VALIDATION_FUNCTION = 'apps.profiler.email.send_validation'
SOCIAL_AUTH_EMAIL_VALIDATION_URL = '/email-sent/'
SOCIAL_AUTH_EMAIL_FORM_HTML = 'email_signup.html'
SOCIAL_AUTH_USERNAME_FORM_HTML = 'username_signup.html'

LOGIN_REDIRECT_URL = '/'
LOGIN_URL = '/login'
LOGIN_ERROR_URL = '/login'
SOCIAL_AUTH_LOGIN_ERROR_URL = '/login'

ACCOUNT_ACTIVATION_DAYS = 7 # One-week activation window; you may, of course, use a different value.
REGISTRATION_AUTO_LOGIN = True # Automatically log the user in.

EMAIL_HOST = 'localhost'
EMAIL_PORT = 1025
EMAIL_HOST_USER = ''
EMAIL_HOST_PASSWORD = ''
EMAIL_USE_TLS = False
DEFAULT_FROM_EMAIL = 'info@google.ru'
EMAIL_FROM = DEFAULT_FROM_EMAIL

EDX_CRETEUSER_URL = 'http://rnoep.raccoongang.com/auth/complete/sso_npoed-oauth2/'

try:
    from local_settings import *
except ImportError:
    print "CRITICAL: You must specify local_settings.py"
    exit()

if RAVEN_CONFIG:
    INSTALLED_APPS += ('raven.contrib.django.raven_compat',)

EDX_API_LOGIN_URL = 'http://%s/auth/login/sso_npoed-oauth2' % EDX_LMS_URL
EDX_COURSES_API = 'http://%s/api/extended/courses/' % EDX_LMS_URL
EDX_ENROLLMENTS_API = 'http://%s/api/enrollment/v1/enrollment' % EDX_LMS_URL
EDX_CRETEUSER_URL = 'http://%s/auth/complete/sso_npoed-oauth2/' % EDX_LMS_URL
