# -*- coding: utf-8 -*-

from django.core.management.base import BaseCommand

from main.models import TournamentGroup, TournamentRound, Venue, Team, Game


class Command(BaseCommand):
    help = 'Creates the real World Cup 2018 data'

    def handle(self, *args, **options):
        self.clear_data()
        self.venues = self.create_venues()
        self.groups = self.create_groups()
        self.rounds = self.create_rounds()
        self.teams = self.create_teams()
        self.create_first_round_games()

    def clear_data(self):
        Game.objects.all().delete()
        TournamentRound.objects.all().delete()
        TournamentGroup.objects.all().delete()
        Team.objects.all().delete()
        Venue.objects.all().delete()

    def create_venues(self):
        venues = {
            # TODO
            # 'saint-denis': Venue(city='Saint-Denis', name='Stade de France', capacity=81338),
        }

        for key, venue in venues.items():
            venue.save()
        return venues

    def create_groups(self):
        groups = {
            # TODO
            # 'a': TournamentGroup(name='Gruppe A', abbreviation='A'),
        }

        for key, group in groups.items():
            group.save()
        return groups

    def create_rounds(self):
        rounds = {
            'vorrunde': TournamentRound(name='Vorrunde', is_knock_out=False, display_order='010', abbreviation='VOR'),
            'achtel': TournamentRound(name='Achtelfinale', is_knock_out=True, display_order='020', abbreviation='AF'),
            'viertel': TournamentRound(name='Viertelfinale', is_knock_out=True, display_order='030', abbreviation='VF'),
            'halb': TournamentRound(name='Halbfinale', is_knock_out=True, display_order='040', abbreviation='HF'),
            'finale': TournamentRound(name='Finale', is_knock_out=True, display_order='050', abbreviation='FIN'),
        }

        for key, round in rounds.items():
            round.save()
        return rounds

    def create_teams(self):
        teams = {
            # TODO
            # 'ALB': Team(name='Albanien', abbreviation='ALB', group=self.groups['a']),
        }

        for key, team in teams.items():
            team.save()
        return teams

    def create_first_round_games(self):
        pass
        # TODO
        # self.a_game('FRA', 'ROU', '2016-06-10 21:00:00+02', 'saint-denis')

    def a_game(self, home, away, kickoff, venue, deadline='2016-06-10 21:00:00+02'):
        hometeam = self.teams[home]
        awayteam = self.teams[away]
        display_name = "%s - %s" % (hometeam, awayteam)
        Game(kickoff=kickoff, deadline=deadline, round=self.rounds['vorrunde'], name=display_name,
             hometeam=hometeam, awayteam=awayteam, venue=self.venues[venue]).save()
