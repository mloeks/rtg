"""Development settings and globals."""

import warnings

from django.utils import timezone

from .base import *

########## DEBUG CONFIGURATION
# See: https://docs.djangoproject.com/en/dev/ref/settings/#debug
DEBUG = True



def zoned_date(*args):
    return datetime.datetime(*args).replace(tzinfo=timezone.get_default_timezone())

# simulate that "now" is a different date
# FAKE_DATE = zoned_date(2018, 10, 30, 9, 0, 0)
# FAKE_DATE = zoned_date(2018, 6, 14, 17, 0, 0)       # World Cup 2018 begins! :-)
# FAKE_DATE = zoned_date(2018, 6, 14, 9, 0, 0)

########## END DEBUG CONFIGURATION

ALLOWED_HOSTS = [
    'localhost', '192.168.2.121'
]

CORS_ORIGIN_REGEX_WHITELIST = ('^(https?://)?(localhost|192.168.2.121):3000$', )

SITE_BASE_URL = 'http://localhost:3000'

########## EMAIL CONFIGURATION
# See: https://docs.djangoproject.com/en/dev/ref/settings/#email-backend
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
EMAIL_HOST = 'localhost'
EMAIL_PORT = 1025
# EMAIL_HOST_USER='username'
# EMAIL_HOST_PASSWORD='password'
EMAIL_USE_TLS = False
EMAIL_PREFIX = '[RTG Local] '
EMAIL_UNDISCLOSED_RECIPIENTS = False
########## END EMAIL CONFIGURATION


########## DATABASE CONFIGURATION
# See: https://docs.djangoproject.com/en/dev/ref/settings/#databases
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'rtg',
        'USER': 'mloeks',
        'PASSWORD': '!Warwickshire',
        'HOST': '127.0.0.1',
        'PORT': '5432',
        # maximum number of seconds to keep the db connection open
        # 0 = re-open the connection at each request (slow)
        # None = keep the connection open forever (maybe performance issues on external system by allowed number of parallel accesses)
        'CONN_MAX_AGE': 10,
    }
}
########## END DATABASE CONFIGURATION


########## CACHE CONFIGURATION
# See: https://docs.djangoproject.com/en/dev/ref/settings/#caches
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
    }
}
########## END CACHE CONFIGURATION


########## REST FRAMEWORK CONFIGURATION
REST_FRAMEWORK['DEFAULT_AUTHENTICATION_CLASSES'] += (
    'rest_framework.authentication.SessionAuthentication',
    'rest_framework.authentication.BasicAuthentication',
)
REST_FRAMEWORK['DEFAULT_RENDERER_CLASSES'] += (
    'rest_framework.renderers.BrowsableAPIRenderer',
)
########## END REST FRAMEWORK CONFIGURATION
