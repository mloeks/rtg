import inspect
import os
import re
import uuid
from datetime import datetime
from enum import Enum

import html2text
from django.conf import settings
from django.contrib.auth.signals import user_logged_in
from django.core.mail import EmailMultiAlternatives
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
        'email': user.email,
        'admin': user.is_staff,
        'has_paid': user.profile.has_paid,
        'avatar': str(user.profile.avatar),
        'no_open_bets': len(user.profile.get_open_bettables()),
        'last_login': last_login,
    }


def extract_homegoals_from_result(result):
    return re.match("^([0-9]{1,2}):[0-9]{1,2}", result).group(1)


def get_reference_date():
    return settings.FAKE_DATE if hasattr(settings, 'FAKE_DATE') else timezone.now()

def extract_awaygoals_from_result(result):
    return re.match("^[0-9]{1,2}:([0-9]{1,2})", result).group(1)


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


def send_mail_to_users(post_instance, force_all=False):
    undisclosed_recipients = settings.EMAIL_UNDISCLOSED_RECIPIENTS
    subject, from_email = settings.EMAIL_PREFIX + post_instance.title, settings.DEFAULT_FROM_EMAIL

    if force_all:
        target_users = active_users().exclude(email=None).exclude(email='')
    else:
        target_users = active_users().exclude(email=None).exclude(email='').filter(profile__daily_emails=True)

    recipients = list(usr.email for usr in target_users)
    recipients.extend(list(usr.profile.email2 for usr in target_users if usr.profile.email2))

    admin_recipients = [tpl[1] for tpl in settings.ADMINS]

    text_content = html2text.html2text(post_instance.content)
    html_content = post_instance.content

    if undisclosed_recipients:
        recipients.extend(admin_recipients)
        msg = EmailMultiAlternatives(subject, text_content, from_email, bcc=recipients)
    else:
        msg = EmailMultiAlternatives(subject, text_content, from_email, to=recipients, bcc=admin_recipients)

    msg.attach_alternative(html_content, "text/html")
    msg.send()


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