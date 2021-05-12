import inspect
import os
import re
import uuid
from enum import Enum

from django.conf import settings
from django.db.models import Q
from django.utils import timezone
from django.utils.text import slugify

from main.models import User


def extract_goals_from_result(result):
    match = re.match("^([0-9]{1,2}):([0-9]{1,2})$", result)
    if match:
        return tuple(int(goal) for goal in match.group(1, 2))
    else:
        return (-1, -1)


def get_reference_date():
    return settings.FAKE_DATE if hasattr(settings, 'FAKE_DATE') else timezone.now()


def game_to_string(game):
    return str(game.hometeam.name) + ' - ' + str(game.awayteam.name)


def get_avatar_path(instance, filename):
    return 'avatars/%s%s' % (uuid.uuid4().hex, os.path.splitext(filename)[1])


def get_thumb_path(instance, filename):
    return 'avatars/%s_t%s' % (slugify(instance.user.username), os.path.splitext(filename)[1])


def sizeof_fmt(num, suffix='B'):
    for unit in ['','K','M','G','T','P','E','Z']:
        if abs(num) < 1024.0:
            return "%3.1f %s%s" % (num, unit, suffix)
        num /= 1024.0
    return "%.1f %s%s" % (num, 'Y', suffix)


def active_users():
    """ Returns users which are active (not disabled) and have logged in this year """
    return User.objects.filter(is_active=True).filter(last_login__year=timezone.now().year)

def inactive_users():
    """ Returns users which are either not active (disabled) OR have not logged in this year """
    return User.objects.filter(Q(is_active=False) | Q(last_login=None) | Q(last_login__year__lt=timezone.now().year))


class ChoicesEnum(Enum):
    """ cf. http://blog.richard.do/index.php/2014/02/how-to-use-enums-for-django-field-choices/ """

    @classmethod
    def choices(cls):
        # get all members of the class
        members = inspect.getmembers(cls, lambda m: not(inspect.isroutine(m)))
        # filter down to just properties
        props = [m for m in members if not(m[0][:2] == '__')]
        # format into django choice tuple
        choices = tuple([(str(p[1].value), p[0]) for p in props])
        return choices