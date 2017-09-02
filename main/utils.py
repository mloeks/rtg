import os
import re

import html2text
from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.utils.text import slugify

from main.models import User


def jwt_response_payload_handler(token, user=None, request=None):
    avatar_prop = user.profile.avatar_cropped
    avatar_url = str(user.profile.avatar_cropped) if avatar_prop else None
    no_open_bets = len(user.profile.get_open_bets()) + len(user.profile.get_open_extras())

    return {
        'token': token,
        'admin': user.is_staff,
        'username': user.username,
        'user_id': user.pk,
        'has_paid': user.profile.has_paid,
        'avatar_url': avatar_url,
        'no_open_bets': no_open_bets
    }


def extract_homegoals_from_result(result):
    return re.match("^([0-9]{1,2}):[0-9]{1,2}", result).group(1)


def extract_awaygoals_from_result(result):
    return re.match("^[0-9]{1,2}:([0-9]{1,2})", result).group(1)


def game_to_string(game):
    return str(game.hometeam.name) + ' - ' + str(game.awayteam.name)


def get_avatar_path(instance, filename):
    return 'avatars/%s_a%s' % (slugify(instance.user.username), os.path.splitext(filename)[1])


def get_thumb_path(instance, filename):
    return 'avatars/%s_t%s' % (slugify(instance.user.username), os.path.splitext(filename)[1])


def send_mail_to_users(post_instance, force_all=False):
    undisclosed_recipients = settings.EMAIL_UNDISCLOSED_RECIPIENTS
    subject, from_email = settings.EMAIL_PREFIX + post_instance.title, settings.DEFAULT_FROM_EMAIL

    if force_all:
        target_users = User.objects.exclude(email=None).exclude(email='').filter(is_active=True)
    else:
        target_users = User.objects.exclude(email=None).exclude(email='').filter(is_active=True)\
            .filter(profile__daily_emails=True)

    recipients = list(usr.email for usr in target_users)
    recipients.extend(list(usr.profile.email2 for usr in target_users if usr.profile.email2))
    recipients.extend(['w.huizing@gmx.net'])

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