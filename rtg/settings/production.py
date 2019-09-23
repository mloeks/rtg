"""Test/Demo settings and globals."""

from __future__ import absolute_import

from django.utils import timezone

from .base import *

########## HOST CONFIGURATION
ALLOWED_HOSTS = [
    '.royale-tippgemeinschaft.de',   # Allow domain and subdomains
]
SITE_BASE_URL = 'https://www.royale-tippgemeinschaft.de'
########## END HOST CONFIGURATION

CORS_ORIGIN_WHITELIST = (
    'https://royale-tippgemeinschaft.de',
    'https://www.royale-tippgemeinschaft.de',
)

########## EMAIL CONFIGURATION
SERVER_EMAIL = 'koenigshaus@royale-tippgemeinschaft.de'
DEFAULT_FROM_EMAIL = SERVER_EMAIL
EMAIL_PREFIX = '[RTG] '
EMAIL_SUBJECT_PREFIX = EMAIL_PREFIX
EMAIL_UNDISCLOSED_RECIPIENTS = True
########## END EMAIL CONFIGURATION

########## DATABASE CONFIGURATION
DATABASES = {
    'default': {
        'ENGINE':'django.db.backends.postgresql',
        'NAME': 'muden_rtg',
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

########## REGISTRATION
REGISTRATION_OPEN = False
########## END REGISTRATION CONFIGURATION

