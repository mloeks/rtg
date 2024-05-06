"""Test/Demo settings and globals."""

from __future__ import absolute_import

from django.utils import timezone

from .base import *

########## HOST CONFIGURATION
ALLOWED_HOSTS = [
    '.demo.royale-tippgemeinschaft.de',   # Allow domain and subdomains
]
SITE_BASE_URL = 'https://demo.royale-tippgemeinschaft.de'
########## END HOST CONFIGURATION

# REST Framework CORS
CORS_ORIGIN_WHITELIST = (
    'https://demo.royale-tippgemeinschaft.de',
    'https://www.demo.royale-tippgemeinschaft.de',
)
# Django Admin CORS
CSRF_TRUSTED_ORIGINS = (
    'https://api.demo.royale-tippgemeinschaft.de',
)

DEBUG = False


def zoned_date(*args):
    return datetime.datetime(*args).replace(tzinfo=timezone.get_default_timezone())

# simulate that "now" is a different date
# FAKE_DATE = zoned_date(2018, 10, 30, 9, 0, 0)


########## EMAIL CONFIGURATION
SERVER_EMAIL = 'koenigshaus@royale-tippgemeinschaft.de'
DEFAULT_FROM_EMAIL = SERVER_EMAIL
EMAIL_PREFIX = '[RTG Demo] '
EMAIL_SUBJECT_PREFIX = EMAIL_PREFIX
EMAIL_UNDISCLOSED_RECIPIENTS = True
########## END EMAIL CONFIGURATION

########## DATABASE CONFIGURATION
DATABASES = {
    'default': {
        'ENGINE':'django.db.backends.postgresql',
        'NAME': 'muden_rtg_demo',
        'USER': 'muden',
        'PASSWORD': 'BX0gLv4N',
        'HOST': '127.0.0.1',
        'PORT': '5432',
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

########## REGISTRATION
REGISTRATION_OPEN = True
########## END REGISTRATION CONFIGURATION

