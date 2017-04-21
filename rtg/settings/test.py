"""Test/Demo settings and globals."""

from __future__ import absolute_import
from django.utils import timezone

from os import environ

from .base import *

# Normally you should not import ANYTHING from Django directly
# into your settings, but ImproperlyConfigured is an exception.
# from django.core.exceptions import ImproperlyConfigured

# def get_env_setting(setting):
#     """ Get the environment setting or return exception """
#     try:
#         return environ[setting]
#     except KeyError:
#         error_msg = "Set the %s env variable" % setting
#         raise ImproperlyConfigured(error_msg)

########## HOST CONFIGURATION
# See: https://docs.djangoproject.com/en/1.5/releases/1.5/#allowed-hosts-required-in-production
ALLOWED_HOSTS = [
    '.demo.royale-tippgemeinschaft.de',   # Allow domain and subdomains
]
########## END HOST CONFIGURATION

DEBUG = True
TEMPLATE_DEBUG = DEBUG

def tz_date(*args):
    return timezone.make_aware(datetime.datetime(*args), timezone.get_default_timezone())

# simulate that "now" is a different date
# FAKE_DATE = tz_date(2016, 10, 30, 9, 0, 0)
# FAKE_DATE = tz_date(2016, 6, 10, 9, 0, 0)       # EURO begins! :-)

CORS_ORIGIN_REGEX_WHITELIST = ('^(https?://)?(\w+\.)?demo.royale-tippgemeinschaft\.de$', )

########## EMAIL CONFIGURATION
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = environ.get('EMAIL_HOST', 'localhost')
EMAIL_HOST_PASSWORD = environ.get('EMAIL_HOST_PASSWORD', '')
EMAIL_HOST_USER = environ.get('EMAIL_HOST_USER', 'matthias@loeks.net')
EMAIL_PORT = environ.get('EMAIL_PORT', 25)
EMAIL_SUBJECT_PREFIX = '[%s] ' % SITE_NAME
EMAIL_USE_TLS = True
SERVER_EMAIL = EMAIL_HOST_USER
EMAIL_PREFIX = '[RTG Demo] '
EMAIL_UNDISCLOSED_RECIPIENTS = True
########## END EMAIL CONFIGURATION

########## DATABASE CONFIGURATION
DATABASES = {
    'default': {
        'ENGINE':'django.db.backends.postgresql_psycopg2',
        'NAME': 'muden_rtg2016_demo',
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

