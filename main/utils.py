import inspect
import os
import re
import uuid
from datetime import datetime
from enum import Enum

from django.conf import settings
from django.contrib.auth.signals import user_logged_in
from django.utils import timezone
from django.utils.text import slugify

from main.models import User


def jwt_response_payload_handler(token, user=None, request=None):
    last_login = None
    if user and request:
        last_login = user.last_login
        user_logged_in.send(sender=user.__class__, request=request, user=user)

    return {
        'token': token,
        'user_id': user.pk,
        'admin': user.is_staff,
        'has_paid': user.profile.has_paid,
        'avatar': str(user.profile.avatar),
        'no_open_bets': len(user.profile.get_open_bettables()),
        'last_login': last_login,
    }


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


def merge_two_dicts(x, y):
    """
        Python < 3.5 compat function for kwargs merging, cf. https://stackoverflow.com/a/26853961
        Given two dicts, merge them into a new dict as a shallow copy.
    """
    z = x.copy()
    z.update(y)
    return z


def sizeof_fmt(num, suffix='B'):
    for unit in ['','K','M','G','T','P','E','Z']:
        if abs(num) < 1024.0:
            return "%3.1f %s%s" % (num, unit, suffix)
        num /= 1024.0
    return "%.1f %s%s" % (num, 'Y', suffix)


def active_users():
    """ Returns users which are active (not disabled) and have logged in this year """
    return User.objects.filter(is_active=True).filter(last_login__year=datetime.now().year)


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