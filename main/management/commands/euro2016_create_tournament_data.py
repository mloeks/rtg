# -*- coding: utf-8 -*-

from django.core.management.base import BaseCommand

from main.models import TournamentGroup, TournamentRound, Venue, Team, Game


class Command(BaseCommand):
    help = 'Creates the real EURO 2016 data'

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
            'saint-denis': Venue(city='Saint-Denis', name='Stade de France', capacity=81338),
            'marseille': Venue(city='Marseille', name='Stade Vélodrome', capacity=67394),
            'lyon': Venue(city='Lyon', name='Parc Olympique Lyonnais', capacity=59286),
            'lille': Venue(city='Lille', name='Stade Pierre-Mauroy', capacity=50186),
            'paris': Venue(city='Paris', name='Parc des Princes', capacity=48712),
            'bordeaux': Venue(city='Bordeaux', name='Nouveau Stade de Bordeaux', capacity=42115),
            'saint-etienne': Venue(city='Saint-Étienne', name='Stade Geoffroy-Guichard', capacity=41965),
            'nizza': Venue(city='Nizza', name='Allianz Riviera', capacity=35624),
            'lens': Venue(city='Lens', name='Stade Bollaert-Delelis', capacity=38223),
            'toulouse': Venue(city='Toulouse', name='Stadium Municipal', capacity=33150)
        }

        for key, venue in venues.items():
            venue.save()
        return venues

    def create_groups(self):
        groups = {
            'a': TournamentGroup(name='Gruppe A', abbreviation='A'),
            'b': TournamentGroup(name='Gruppe B', abbreviation='B'),
            'c': TournamentGroup(name='Gruppe C', abbreviation='C'),
            'd': TournamentGroup(name='Gruppe D', abbreviation='D'),
            'e': TournamentGroup(name='Gruppe E', abbreviation='E'),
            'f': TournamentGroup(name='Gruppe F', abbreviation='F')
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
            'ALB': Team(name='Albanien', abbreviation='ALB', group=self.groups['a']),
            'FRA': Team(name='Frankreich', abbreviation='FRA', group=self.groups['a']),
            'ROU': Team(name='Rumänien', abbreviation='ROU', group=self.groups['a']),
            'SUI': Team(name='Schweiz', abbreviation='SUI', group=self.groups['a']),

            'ENG': Team(name='England', abbreviation='ENG', group=self.groups['b']),
            'RUS': Team(name='Russland', abbreviation='RUS', group=self.groups['b']),
            'SVK': Team(name='Slowakei', abbreviation='SVK', group=self.groups['b']),
            'WAL': Team(name='Wales', abbreviation='WAL', group=self.groups['b']),

            'GER': Team(name='Deutschland', abbreviation='GER', group=self.groups['c']),
            'NIR': Team(name='Nordirland', abbreviation='NIR', group=self.groups['c']),
            'POL': Team(name='Polen', abbreviation='POL', group=self.groups['c']),
            'UKR': Team(name='Ukraine', abbreviation='UKR', group=self.groups['c']),

            'CRO': Team(name='Kroatien', abbreviation='CRO', group=self.groups['d']),
            'CZE': Team(name='Tschechien', abbreviation='CZE', group=self.groups['d']),
            'ESP': Team(name='Spanien', abbreviation='ESP', group=self.groups['d']),
            'TUR': Team(name='Türkei', abbreviation='TUR', group=self.groups['d']),

            'BEL': Team(name='Belgien', abbreviation='BEL', group=self.groups['e']),
            'ITA': Team(name='Italien', abbreviation='ITA', group=self.groups['e']),
            'IRL': Team(name='Irland', abbreviation='IRL', group=self.groups['e']),
            'SWE': Team(name='Schweden', abbreviation='SWE', group=self.groups['e']),

            'AUT': Team(name='Österreich', abbreviation='AUT', group=self.groups['f']),
            'HUN': Team(name='Ungarn', abbreviation='HUN', group=self.groups['f']),
            'ISL': Team(name='Island', abbreviation='ISL', group=self.groups['f']),
            'POR': Team(name='Portugal', abbreviation='POR', group=self.groups['f'])
        }

        for key, team in teams.items():
            team.save()
        return teams

    def create_first_round_games(self):
        self.a_game('FRA', 'ROU', '2016-06-10 21:00:00+02', 'saint-denis')
        self.a_game('ALB', 'SUI', '2016-06-11 15:00:00+02', 'lens')
        self.a_game('WAL', 'SVK', '2016-06-11 18:00:00+02', 'bordeaux')
        self.a_game('ENG', 'RUS', '2016-06-11 21:00:00+02', 'marseille')
        self.a_game('TUR', 'CRO', '2016-06-12 15:00:00+02', 'paris')
        self.a_game('POL', 'NIR', '2016-06-12 18:00:00+02', 'nizza')
        self.a_game('GER', 'UKR', '2016-06-12 21:00:00+02', 'lille')
        self.a_game('ESP', 'CZE', '2016-06-13 15:00:00+02', 'toulouse')
        self.a_game('IRL', 'SWE', '2016-06-13 18:00:00+02', 'saint-denis')
        self.a_game('BEL', 'ITA', '2016-06-13 21:00:00+02', 'lyon')
        self.a_game('AUT', 'HUN', '2016-06-14 18:00:00+02', 'bordeaux')
        self.a_game('POR', 'ISL', '2016-06-14 21:00:00+02', 'saint-etienne')

        self.a_game('RUS', 'SVK', '2016-06-15 15:00:00+02', 'lille')
        self.a_game('ROU', 'SUI', '2016-06-15 18:00:00+02', 'paris')
        self.a_game('FRA', 'ALB', '2016-06-15 21:00:00+02', 'marseille')
        self.a_game('ENG', 'WAL', '2016-06-16 15:00:00+02', 'lens')
        self.a_game('UKR', 'NIR', '2016-06-16 18:00:00+02', 'lyon')
        self.a_game('GER', 'POL', '2016-06-16 21:00:00+02', 'saint-denis')
        self.a_game('ITA', 'SWE', '2016-06-17 15:00:00+02', 'toulouse')
        self.a_game('CZE', 'CRO', '2016-06-17 18:00:00+02', 'saint-etienne')
        self.a_game('ESP', 'TUR', '2016-06-17 21:00:00+02', 'nizza')
        self.a_game('BEL', 'IRL', '2016-06-18 15:00:00+02', 'bordeaux')
        self.a_game('ISL', 'HUN', '2016-06-18 18:00:00+02', 'marseille')
        self.a_game('POR', 'AUT', '2016-06-18 21:00:00+02', 'paris')

        self.a_game('ROU', 'ALB', '2016-06-19 21:00:00+02', 'lyon')
        self.a_game('SUI', 'FRA', '2016-06-19 21:00:00+02', 'lille')
        self.a_game('RUS', 'WAL', '2016-06-20 21:00:00+02', 'toulouse')
        self.a_game('SVK', 'ENG', '2016-06-20 21:00:00+02', 'saint-etienne')
        self.a_game('UKR', 'POL', '2016-06-21 18:00:00+02', 'marseille')
        self.a_game('NIR', 'GER', '2016-06-21 18:00:00+02', 'paris')
        self.a_game('CZE', 'TUR', '2016-06-21 21:00:00+02', 'lens')
        self.a_game('CRO', 'ESP', '2016-06-21 21:00:00+02', 'bordeaux')
        self.a_game('ISL', 'AUT', '2016-06-22 18:00:00+02', 'saint-denis')
        self.a_game('HUN', 'POR', '2016-06-22 18:00:00+02', 'lyon')
        self.a_game('ITA', 'IRL', '2016-06-22 21:00:00+02', 'lille')
        self.a_game('SWE', 'BEL', '2016-06-22 21:00:00+02', 'nizza')

    def a_game(self, home, away, kickoff, venue, deadline='2016-06-10 21:00:00+02'):
        hometeam = self.teams[home]
        awayteam = self.teams[away]
        Game(kickoff=kickoff, deadline=deadline, round=self.rounds['vorrunde'],
             hometeam=hometeam, awayteam=awayteam, venue=self.venues[venue]).save()
