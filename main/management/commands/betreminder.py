# -*- coding: utf-8 -*-
import logging
from datetime import timedelta

from main.mail_utils import with_rtg_template
from main.utils import active_users

__author__ = 'mloeks'

from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.core.management.base import BaseCommand
from django.template.loader import render_to_string

LOG = logging.getLogger('rtg.' + __name__)


class Command(BaseCommand):
    args = ''
    help = 'Daily reminder e-mails for RTG members'

    def handle(self, *args, **options):
        self.send_bet_reminder()

    def send_bet_reminder(self):
        LOG.info('Running bet reminder...')
        for user in active_users().filter(profile__reminder_emails=True).order_by('username'):
            open_bettables = user.profile.get_open_bettables_deadline_within(timedelta(hours=30))
            if open_bettables:
                ctx = {'user': user, 'open_bettables': open_bettables}

                subject = 'Tipp-Erinnerung'
                subject = settings.EMAIL_PREFIX + subject

                print("Sending reminder E-Mail to " + str(user.username) + " [" + str(user.email) + "]...")
                LOG.info("Sending reminder E-Mail to " + str(user.username) + " [" + str(user.email) + "]...")

                text_content = render_to_string('rtg/bet_reminder_email.html', ctx)
                html_content = with_rtg_template({'subtitle': 'Tipp-Erinnerung', 'content': text_content})

                mail = EmailMultiAlternatives(subject, text_content, settings.DEFAULT_FROM_EMAIL, [user.email],
                                              bcc=['admin@royale-tippgemeinschaft.de'])
                mail.attach_alternative(html_content, "text/html")
                mail.send()
        LOG.info('Bet reminder done.')
