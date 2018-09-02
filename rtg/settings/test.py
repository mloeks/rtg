"""Test/Demo settings and globals."""

from __future__ import absolute_import

from django.utils import timezone

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
SITE_BASE_URL = 'https://demo.royale-tippgemeinschaft.de'
########## END HOST CONFIGURATION

CORS_ORIGIN_WHITELIST = (
    'demo.royale-tippgemeinschaft.de',
    'www.demo.royale-tippgemeinschaft.de',
)

DEBUG = True

def tz_date(*args):
    return timezone.make_aware(datetime.datetime(*args), timezone.get_default_timezone())

# simulate that "now" is a different date
# FAKE_DATE = tz_date(2018, 10, 30, 9, 0, 0)
# FAKE_DATE = tz_date(2018, 6, 14, 17, 0, 0)       # World Cup 2018 begins! :-)

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

