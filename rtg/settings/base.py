"""Common settings and globals."""
import datetime

import os

from os.path import abspath, basename, dirname, join, normpath
from sys import path

from django.core.exceptions import ImproperlyConfigured


########## PATH CONFIGURATION
# Absolute filesystem path to the Django project directory:
DJANGO_ROOT = dirname(dirname(abspath(__file__)))

# Absolute filesystem path to the top-level project folder:
SITE_ROOT = dirname(DJANGO_ROOT)

# Site name:
SITE_NAME = basename(DJANGO_ROOT)

# Add our project to our pythonpath, this way we don't need to type our project
# name in our dotted import paths:
path.append(DJANGO_ROOT)
########## END PATH CONFIGURATION


########## DEBUG CONFIGURATION
# See: https://docs.djangoproject.com/en/dev/ref/settings/#debug
DEBUG = False
########## END DEBUG CONFIGURATION


########## MANAGER CONFIGURATION
# See: https://docs.djangoproject.com/en/dev/ref/settings/#admins
ADMINS = (
    ('RTG Admin', 'admin@royale-tippgemeinschaft.de'),
)

DEFAULT_FROM_EMAIL = 'koenigshaus@royale-tippgemeinschaft.de'
DEFAULT_STAFF_EMAIL = DEFAULT_FROM_EMAIL

# See: https://docs.djangoproject.com/en/dev/ref/settings/#managers
MANAGERS = ADMINS
########## END MANAGER CONFIGURATION

########## GENERAL CONFIGURATION
TIME_ZONE = 'Europe/Berlin'
LANGUAGE_CODE = 'de'
SITE_ID = 1
USE_I18N = True
USE_L10N = True
USE_TZ = True
########## END GENERAL CONFIGURATION

########## MEDIA CONFIGURATION
MEDIA_ROOT = normpath(join(SITE_ROOT, 'media'))
MEDIA_URL = '/media/'
########## END MEDIA CONFIGURATION


########## STATIC FILE CONFIGURATION
# See: https://docs.djangoproject.com/en/dev/ref/settings/#static-root
STATIC_ROOT = normpath(join(SITE_ROOT, 'assets'))
STATIC_URL = '/static/'
STATICFILES_DIRS = (
    normpath(join(SITE_ROOT, 'static')),
)

# See: https://docs.djangoproject.com/en/dev/ref/contrib/staticfiles/#staticfiles-finders
STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
    # 'compressor.finders.CompressorFinder',
)
########## END STATIC FILE CONFIGURATION


########## SECRET CONFIGURATION
# See: https://docs.djangoproject.com/en/dev/ref/settings/#secret-key

def get_env_variable(var_name):
    """Get the environment variable or return exception."""
    try:
        return os.environ[var_name]
    except KeyError:
        error_msg = "Set the %s environment variable" % var_name
        raise ImproperlyConfigured(error_msg)

SECRET_KEY = get_env_variable('SECRET_KEY_RTG')

########## END SECRET CONFIGURATION


########## SITE CONFIGURATION
# Hosts/domain names that are valid for this site
# See https://docs.djangoproject.com/en/1.5/ref/settings/#allowed-hosts
ALLOWED_HOSTS = [
    '.royale-tippgemeinschaft.de'
]
########## END SITE CONFIGURATION


########## FIXTURE CONFIGURATION
# See: https://docs.djangoproject.com/en/dev/ref/settings/#std:setting-FIXTURE_DIRS
FIXTURE_DIRS = (
    normpath(join(SITE_ROOT, 'fixtures')),
)
########## END FIXTURE CONFIGURATION


########## TEMPLATE CONFIGURATION
# https://docs.djangoproject.com/en/1.11/ref/templates/upgrading/
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            normpath(join(SITE_ROOT, 'rtg/templates')),
        ],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.contrib.auth.context_processors.auth',
                'django.template.context_processors.debug',
                'django.template.context_processors.i18n',
                'django.template.context_processors.media',
                'django.template.context_processors.static',
                'django.template.context_processors.tz',
                'django.contrib.messages.context_processors.messages',
                'django.template.context_processors.request',
            ],
        },
    },
]
########## END TEMPLATE CONFIGURATION


########## MIDDLEWARE CONFIGURATION
# See: https://docs.djangoproject.com/en/dev/ref/settings/#middleware-classes
# Migration cf. https://docs.djangoproject.com/en/1.11/topics/http/middleware/#upgrading-middleware
MIDDLEWARE = (
    # Default Django middleware.
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'corsheaders.middleware.CorsMiddleware',
)
########## END MIDDLEWARE CONFIGURATION


########## URL CONFIGURATION
# See: https://docs.djangoproject.com/en/dev/ref/settings/#root-urlconf
ROOT_URLCONF = '%s.urls' % SITE_NAME
########## END URL CONFIGURATION


########## APP CONFIGURATION
DJANGO_APPS = (
    # Default Django apps:
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # Useful template tags:
    # 'django.contrib.humanize',

    # Admin panel and documentation:
    'django.contrib.admin',
    # 'django.contrib.admindocs',

    'django_filters',
)

# Apps specific for this project go here.
LOCAL_APPS = (
    'main',
    'rest_framework',
    'rest_framework.authtoken',
    'rest_auth',
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'rest_auth.registration',
    'corsheaders'
)

# See: https://docs.djangoproject.com/en/dev/ref/settings/#installed-apps
INSTALLED_APPS = DJANGO_APPS + LOCAL_APPS
########## END APP CONFIGURATION


########## LOGGING CONFIGURATION
# See: https://docs.djangoproject.com/en/dev/ref/settings/#logging
LOGGING = {
    'version': 1,
    'disable_existing_loggers': True,
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse'
        }
    },
    'formatters': {
        'default': {
            # possible attributes: https://docs.python.org/3/library/logging.html#logrecord-attributes
            'format': '%(asctime)s [%(name)s] %(levelname)s - %(message)s',
            'datefmt': '%Y-%m-%d %H:%M:%S'
        },
    },
    'handlers': {
        'mail_admins': {
            'level': 'ERROR',
            'filters': ['require_debug_false'],
            'class': 'django.utils.log.AdminEmailHandler'
        },
        'application_log': {
            'level': 'INFO',
            'class': 'logging.handlers.TimedRotatingFileHandler',
            'filename': os.path.join(SITE_ROOT, 'log/rtg_app.log'),
            'when': 'midnight',
            'backupCount': 10,
            'formatter': 'default'
        },
    },
    'loggers': {
        'django.request': {
            'handlers': ['mail_admins'],
            'level': 'ERROR',
            'propagate': True,
        },
        'rtg': {
            'handlers': ['application_log'],
            'level': 'INFO',
            'propagate': False
        },
    }
}
########## END LOGGING CONFIGURATION


########## WSGI CONFIGURATION
# See: https://docs.djangoproject.com/en/dev/ref/settings/#wsgi-application
WSGI_APPLICATION = 'wsgi.application'
########## END WSGI CONFIGURATION

# auth settings
# PASSWORD_RESET_TIMEOUT_DAYS = 1

# rest-auth settings
OLD_PASSWORD_FIELD_ENABLED = True
LOGOUT_ON_PASSWORD_CHANGE = False
REST_AUTH_SERIALIZERS = {
    'PASSWORD_RESET_CONFIRM_SERIALIZER': 'main.registration_overrides.RtgPasswordResetConfirmSerializer'
}

# all-auth settings
# ACCOUNT_AUTHENTICATION_METHOD = "username_email"
ACCOUNT_EMAIL_VERIFICATION = "optional"
ACCOUNT_USERNAME_MIN_LENGTH = 3
ACCOUNT_USERNAME_REQUIRED = True
ACCOUNT_USERNAME_VALIDATORS = 'main.registration_overrides.rtg_username_validators'

# allow for e-mail as user name (EmailBackend)
AUTHENTICATION_BACKENDS = (
    'rtg.backends.EmailBackend',
    'django.contrib.auth.backends.ModelBackend',
)


########## REST FRAMEWORK CONFIGURATION
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': ('rest_framework_jwt.authentication.JSONWebTokenAuthentication',),
    'DEFAULT_PERMISSION_CLASSES': ('rest_framework.permissions.IsAuthenticated',),
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.LimitOffsetPagination',
    'DEFAULT_RENDERER_CLASSES': ('rest_framework.renderers.JSONRenderer',),
    'PAGE_SIZE': 25,
    'UPLOADED_FILES_USE_URL': False
}
REST_SESSION_LOGIN = False
JWT_AUTH = {
    'JWT_AUTH_HEADER_PREFIX': 'Token',
    'JWT_RESPONSE_PAYLOAD_HANDLER': 'main.utils.jwt_response_payload_handler',
    'JWT_EXPIRATION_DELTA': datetime.timedelta(hours=4),
    'JWT_ALLOW_REFRESH': True,
    'JWT_REFRESH_EXPIRATION_DELTA': datetime.timedelta(hours=12),
}
########## END REST FRAMEWORK CONFIGURATION

########## REGISTRATION
REGISTRATION_OPEN = True
########## END REGISTRATION CONFIGURATION

# 2.5MB - 2621440
# 3MB - 3145728
# 5MB - 5242880
# 10MB - 10485760
# 20MB - 20971520
# 50MB - 5242880
# 100MB 104857600
# 250MB - 214958080
# 500MB - 429916160
MAX_UPLOAD_SIZE = 5242880