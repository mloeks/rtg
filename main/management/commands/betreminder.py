# -*- coding: utf-8 -*-
__author__ = 'mloeks'

from datetime import *

from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.core.management.base import BaseCommand
from django.template.loader import render_to_string
from django.utils import timezone

from main.models import User


class Command(BaseCommand):
    args = ''
    help = 'Daily reminder e-mails for RTG members'

    def handle(self, *args, **options):
        self.send_bet_reminder()

    def send_bet_reminder(self):
        for user in User.objects.filter(is_active=True).filter(profile__reminder_emails=True).order_by('username'):
            open_bet_games = self.get_open_bet_games(user)
            open_bet_extras = self.get_open_bet_extras(user)
            if open_bet_games or open_bet_extras:
                ctx = {'user': user, 'games_to_bet': open_bet_games, 'extras_to_bet': open_bet_extras}

                subject = 'Tipp-Erinnerung'
                subject = settings.EMAIL_PREFIX + subject

                message = render_to_string('rtg/bet_reminder_email.html', ctx)
                print("Sending reminder E-Mail to " + str(user.username) + " [" + str(user.email) + "]...")
                mail = EmailMultiAlternatives(subject, message, settings.DEFAULT_FROM_EMAIL, [user.email],
                                              bcc=['admin@royale-tippgemeinschaft.de'])
                mail.send()

    def get_open_bet_games(self, user):
        ret = []
        ref_date = settings.FAKE_DATE if hasattr(settings, 'FAKE_DATE') else timezone.now()
        for open_bet in user.profile.get_open_bets():
            delta = open_bet.deadline - ref_date
            if 0 <= delta.days < 1 and 0 < delta.seconds <= 24*3600:
                ret.append(open_bet)
        return ret

    def get_open_bet_extras(self, user):
        ret = []
        ref_date = settings.FAKE_DATE if hasattr(settings, 'FAKE_DATE') else timezone.now()
        for open_bet in user.profile.get_open_extras():
            delta = open_bet.deadline - ref_date
            if 0 <= delta.days < 1 and 0 < delta.seconds <= 24*3600:
                ret.append(open_bet)
        return ret