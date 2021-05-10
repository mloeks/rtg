# -*- coding: utf-8 -*-

from django.core.management.base import BaseCommand

from main.models import TournamentGroup, TournamentRound, Venue, Team, Game, Extra, Bet, Bettable


class Command(BaseCommand):
    help = 'Clears tournament data (teams, games, bets etc.) but KEEPS users and posts'

    def handle(self, *args, **options):
        TournamentRound.objects.all().delete()
        TournamentGroup.objects.all().delete()
        Team.objects.all().delete()
        Venue.objects.all().delete()
        Bet.objects.all().delete()
        Game.objects.all().delete()
        Extra.objects.all().delete()
        Bettable.objects.all().delete()
