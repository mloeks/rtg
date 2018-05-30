# -*- coding: utf-8 -*-
import random
from datetime import datetime, timedelta

from django.core.management.base import BaseCommand

from main.models import TournamentRound, Venue, Team, Game, Bettable


class Command(BaseCommand):
    help = 'Creates some test games (in the quarter final round) around the current date'

    def add_arguments(self, parser):
        parser.add_argument('number_games')

    def handle(self, *args, **options):
        nr_games = int(options['number_games']) or 5
        self.create_games(nr_games)

    def create_games(self, count):
        for i in range(-2, -2 + count):
            all_teams = Team.objects.all()
            random_hometeam = random.choice(all_teams)
            random_awayteam = random.choice(all_teams)

            kickoff = datetime.now() + timedelta(days=i, hours=-1)
            Game(kickoff=kickoff, deadline=kickoff, round=TournamentRound.objects.get(abbreviation='VF'),
                 hometeam=random_hometeam, awayteam=random_awayteam, venue=random.choice(Venue.objects.all()),
                 homegoals=3 if i < 0 else -1, awaygoals=2 if i < 0 else -1).save()
