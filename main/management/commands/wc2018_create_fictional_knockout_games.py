# -*- coding: utf-8 -*-

from django.core.management.base import BaseCommand

from main.models import Game, Team, TournamentRound, Venue


class Command(BaseCommand):
    help = 'Creates some fictive World Cup 2018 knock out round games'

    def handle(self, *args, **options):
        Game.objects.exclude(round__name='Vorrunde').all().delete()
        self.create_some_knockout_games()

    def create_some_knockout_games(self):
        self.a_game('RUS', 'KSA', 'AF', '2018-06-30 17:00:00+02', 'Sotschi')
        self.a_game('EGY', 'URU', 'AF', '2018-07-01 14:00:00+02', 'Jekaterinburg')
        self.a_game('GER', 'ESP', 'AF', '2018-07-01 17:00:00+02', 'Kasan')

        self.a_game('BRA', 'FRA', 'HF', '2018-07-05 20:00:00+02', 'Kaliningrad')
        self.a_game('POR', 'GER', 'HF', '2018-07-06 20:00:00+02', 'Sankt Petersburg')

        self.a_game('GER', 'BRA', 'FIN', '2018-07-12 19:00:00+02', 'Moskau (Luschniki)')

    def a_game(self, home, away, round_abbreviation, kickoff, venue_city):
        hometeam = Team.objects.get(abbreviation=home)
        awayteam = Team.objects.get(abbreviation=away)
        round = TournamentRound.objects.get(abbreviation=round_abbreviation)
        venue = Venue.objects.get(city=venue_city)

        Game(kickoff=kickoff, deadline=kickoff, round=round, hometeam=hometeam, awayteam=awayteam, venue=venue).save()
