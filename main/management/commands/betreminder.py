# -*- coding: utf-8 -*-
from datetime import timedelta

from utils import active_users

__author__ = 'mloeks'

from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.core.management.base import BaseCommand
from django.template.loader import render_to_string


# TODO P1 add cron to server
class Command(BaseCommand):
    args = ''
    help = 'Daily reminder e-mails for RTG members'

    def handle(self, *args, **options):
        self.send_bet_reminder()

    def send_bet_reminder(self):
        for user in active_users().filter(profile__reminder_emails=True).order_by('username'):
            open_bettables = user.profile.get_open_bettables_deadline_within(timedelta(hours=24))
            if open_bettables:
                ctx = {'user': user, 'open_bettables': open_bettables}

                subject = 'Tipp-Erinnerung'
                subject = settings.EMAIL_PREFIX + subject

                message = render_to_string('rtg/bet_reminder_email.html', ctx)
                print("Sending reminder E-Mail to " + str(user.username) + " [" + str(user.email) + "]...")
                mail = EmailMultiAlternatives(subject, message, settings.DEFAULT_FROM_EMAIL, [user.email],
                                              bcc=['admin@royale-tippgemeinschaft.de'])
                mail.send()
