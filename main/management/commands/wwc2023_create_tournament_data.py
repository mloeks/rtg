# -*- coding: utf-8 -*-

from django.core.management.base import BaseCommand

from main.models import TournamentGroup, TournamentRound, Venue, Team, Game, Extra, ExtraChoice


class Command(BaseCommand):
    help = 'Creates the real WWC 2023 data'

    TOURNAMENT_START = '2023-07-20 19:00:00+12'

    def handle(self, *args, **options):
        self.clear_data()
        self.venues = self.create_venues()
        self.groups = self.create_groups()
        self.rounds = self.create_rounds()
        self.teams = self.create_teams()
        self.create_first_round_games()
        self.create_extra_bets()

    def clear_data(self):
        Game.objects.all().delete()
        Extra.objects.all().delete()
        ExtraChoice.objects.all().delete()
        TournamentRound.objects.all().delete()
        TournamentGroup.objects.all().delete()
        Team.objects.all().delete()
        Venue.objects.all().delete()

    def create_venues(self):
        venues = {
            'sydney_big': Venue(city='Sydney', name='Stadium Australia', capacity=83500),
            'sydney_small': Venue(city='Sydney', name='Sydney Football Stadium', capacity=42512),
            'brisbane': Venue(city='Brisbane', name='Lang Park', capacity=52263),
            'melbourne': Venue(city='Melbourne', name='Melbourne Rectangular Stadium', capacity=30052),
            'perth': Venue(city='Perth', name='Perth Rectangular Stadium', capacity=22225),
            'adelaide': Venue(city='Adelaide', name='Hindmarsh Stadium', capacity=18435),
            'auckland': Venue(city='Auckland', name='Eden Park', capacity=48276),
            'wellington': Venue(city='Wellington', name='Wellington Regional Stadium', capacity=39000),
            'dunedin': Venue(city='Dunedin', name='Forsyth Barr Stadium', capacity=28744),
            'hamilton': Venue(city='Hamilton', name='Waikato Stadium', capacity=25111),
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
            'f': TournamentGroup(name='Gruppe F', abbreviation='F'),
            'g': TournamentGroup(name='Gruppe G', abbreviation='G'),
            'h': TournamentGroup(name='Gruppe H', abbreviation='H'),
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
            'platz3': TournamentRound(name='Spiel um Platz 3', is_knock_out=True, display_order='050', abbreviation='SP3'),
            'finale': TournamentRound(name='Finale', is_knock_out=True, display_order='060', abbreviation='FIN'),
        }

        for key, round in rounds.items():
            round.save()
        return rounds

    # Country codes according to official FIFA code list
    # See https://de.wikipedia.org/wiki/FIFA-L%C3%A4ndercode
    def create_teams(self):
        teams = {
            'NZL': Team(name='Neuseeland', abbreviation='NZL', group=self.groups['a']),
            'NOR': Team(name='Norwegen', abbreviation='NOR', group=self.groups['a']),
            'PHI': Team(name='Philippinen', abbreviation='PHI', group=self.groups['a']),
            'SUI': Team(name='Schweiz', abbreviation='SUI', group=self.groups['a']),

            'AUS': Team(name='Australien', abbreviation='AUS', group=self.groups['b']),
            'IRL': Team(name='Irland', abbreviation='IRL', group=self.groups['b']),
            'CAN': Team(name='Kanada', abbreviation='CAN', group=self.groups['b']),
            'NGA': Team(name='Nigeria', abbreviation='NGA', group=self.groups['b']),

            'CRC': Team(name='Costa Rica', abbreviation='CRC', group=self.groups['c']),
            'JPN': Team(name='Japan', abbreviation='JPN', group=self.groups['c']),
            'ZAM': Team(name='Sambia', abbreviation='ZAM', group=self.groups['c']),
            'ESP': Team(name='Spanien', abbreviation='ESP', group=self.groups['c']),

            'CHN': Team(name='China', abbreviation='CHN', group=self.groups['d']),
            'DEN': Team(name='Dänemark', abbreviation='DEN', group=self.groups['d']),
            'ENG': Team(name='England', abbreviation='ENG', group=self.groups['d']),
            'HAI': Team(name='Haiti', abbreviation='HAI', group=self.groups['d']),

            'USA': Team(name='USA', abbreviation='USA', group=self.groups['e']),
            'VIE': Team(name='Vietnam', abbreviation='VIE', group=self.groups['e']),
            'NED': Team(name='Niederlande', abbreviation='NED', group=self.groups['e']),
            'POR': Team(name='Portugal', abbreviation='POR', group=self.groups['e']),

            'FRA': Team(name='Frankreich', abbreviation='FRA', group=self.groups['f']),
            'JAM': Team(name='Jamaika', abbreviation='JAM', group=self.groups['f']),
            'BRA': Team(name='Brasilien', abbreviation='BRA', group=self.groups['f']),
            'PAN': Team(name='Panama', abbreviation='PAN', group=self.groups['f']),

            'SWE': Team(name='Schweden', abbreviation='SWE', group=self.groups['g']),
            'RSA': Team(name='Südafrika', abbreviation='KSA', group=self.groups['g']),
            'ITA': Team(name='Italien', abbreviation='ITA', group=self.groups['g']),
            'ARG': Team(name='Argentinien', abbreviation='ARG', group=self.groups['g']),

            'GER': Team(name='Deutschland', abbreviation='GER', group=self.groups['h']),
            'MAR': Team(name='Marokko', abbreviation='MAR', group=self.groups['h']),
            'COL': Team(name='Kolumbien', abbreviation='COL', group=self.groups['h']),
            'KOR': Team(name='Südkorea', abbreviation='KOR', group=self.groups['h']),
        }

        for key, team in teams.items():
            team.save()
        return teams

    def create_first_round_games(self):
        self.a_game('NZL', 'NOR', self.TOURNAMENT_START, 'auckland')
        self.a_game('PHI', 'SUI', '2023-07-21 17:00:00+12', 'dunedin')
        self.a_game('NZL', 'PHI', '2023-07-25 17:30:00+12', 'wellington')
        self.a_game('SUI', 'NOR', '2023-07-25 20:00:00+12', 'hamilton')
        self.a_game('SUI', 'NZL', '2023-07-30 19:00:00+12', 'dunedin')
        self.a_game('NOR', 'PHI', '2023-07-30 19:00:00+12', 'auckland')

        self.a_game('AUS', 'IRL', '2023-07-20 20:00:00+10', 'sydney_small')
        self.a_game('NGA', 'CAN', '2023-07-21 12:30:00+10', 'melbourne')
        self.a_game('CAN', 'IRL', '2023-07-26 20:00:00+08', 'perth')
        self.a_game('AUS', 'NGA', '2023-07-27 20:00:00+10', 'brisbane')
        self.a_game('CAN', 'AUS', '2023-07-31 20:00:00+10', 'melbourne')
        self.a_game('IRL', 'NGA', '2023-07-31 20:00:00+10', 'brisbane')

        self.a_game('ESP', 'CRC', '2023-07-21 19:30:00+12', 'wellington')
        self.a_game('ZAM', 'JPN', '2023-07-22 19:00:00+12', 'hamilton')
        self.a_game('JPN', 'CRC', '2023-07-26 17:00:00+12', 'dunedin')
        self.a_game('ESP', 'ZAM', '2023-07-26 19:30:00+12', 'auckland')
        self.a_game('JPN', 'ESP', '2023-07-31 19:00:00+12', 'wellington')
        self.a_game('CRC', 'ZAM', '2023-07-31 19:00:00+12', 'hamilton')

        self.a_game('ENG', 'HAI', '2023-07-22 19:30:00+10', 'brisbane')
        self.a_game('DEN', 'CHN', '2023-07-22 20:00:00+08', 'perth')
        self.a_game('ENG', 'DEN', '2023-07-28 18:30:00+10', 'sydney_small')
        self.a_game('CHN', 'HAI', '2023-07-28 20:30:00+09:30', 'adelaide')
        self.a_game('CHN', 'ENG', '2023-08-01 20:30:00+09:30', 'adelaide')
        self.a_game('HAI', 'DEN', '2023-08-01 19:00:00+08', 'perth')

        self.a_game('USA', 'VIE', '2023-07-22 13:00:00+12', 'auckland')
        self.a_game('NED', 'POR', '2023-07-23 19:30:00+12', 'dunedin')
        self.a_game('USA', 'NED', '2023-07-27 13:00:00+12', 'wellington')
        self.a_game('POR', 'VIE', '2023-07-27 19:30:00+12', 'hamilton')
        self.a_game('POR', 'USA', '2023-08-01 19:00:00+12', 'auckland')
        self.a_game('VIE', 'NED', '2023-08-01 19:00:00+12', 'dunedin')

        self.a_game('FRA', 'JAM', '2023-07-23 20:00:00+10', 'sydney_small')
        self.a_game('BRA', 'PAN', '2023-07-24 20:30:00+09:30', 'adelaide')
        self.a_game('FRA', 'BRA', '2023-07-29 20:00:00+10', 'brisbane')
        self.a_game('PAN', 'JAM', '2023-07-29 20:30:00+08', 'perth')
        self.a_game('PAN', 'FRA', '2023-08-02 20:00:00+10', 'sydney_small')
        self.a_game('JAM', 'BRA', '2023-08-02 20:00:00+10', 'melbourne')

        self.a_game('SWE', 'RSA', '2023-07-23 17:00:00+12', 'wellington')
        self.a_game('ITA', 'ARG', '2023-07-24 18:00:00+12', 'auckland')
        self.a_game('ARG', 'RSA', '2023-07-28 12:00:00+12', 'dunedin')
        self.a_game('SWE', 'ITA', '2023-07-29 19:30:00+12', 'wellington')
        self.a_game('ARG', 'SWE', '2023-08-02 19:00:00+12', 'hamilton')
        self.a_game('RSA', 'ITA', '2023-08-02 19:00:00+12', 'wellington')

        self.a_game('GER', 'MAR', '2023-07-24 18:30:00+10', 'melbourne')
        self.a_game('COL', 'KOR', '2023-07-25 12:00:00+10', 'sydney_small')
        self.a_game('KOR', 'MAR', '2023-07-30 14:00:00+09:30', 'adelaide')
        self.a_game('GER', 'COL', '2023-07-30 19:30:00+10', 'sydney_small')
        self.a_game('KOR', 'GER', '2023-08-03 20:00:00+10', 'brisbane')
        self.a_game('MAR', 'COL', '2023-08-03 18:00:00+08', 'perth')

    def create_extra_bets(self):
        winner = Extra(name='Wer wird Weltmeister?', points=5, deadline=self.TOURNAMENT_START)
        deu = Extra(name='Wie weit kommt Deutschland?', points=5, deadline=self.TOURNAMENT_START)
        winner.save()
        deu.save()

        for team in Team.objects.all():
            ExtraChoice(name=team.name, extra=winner, sort_index=team.name[0:9]).save()

        ExtraChoice(name='Vorrunde', extra=deu, sort_index='010').save()
        ExtraChoice(name='Achtelfinale', extra=deu, sort_index='020').save()
        ExtraChoice(name='Viertelfinale', extra=deu, sort_index='030').save()
        ExtraChoice(name='Vierter', extra=deu, sort_index='040').save()
        ExtraChoice(name='Dritter', extra=deu, sort_index='050').save()
        ExtraChoice(name='Zweiter', extra=deu, sort_index='060').save()
        ExtraChoice(name='Weltmeister', extra=deu, sort_index='070').save()

    def a_game(self, home, away, kickoff, venue, deadline=TOURNAMENT_START):
        hometeam = self.teams[home]
        awayteam = self.teams[away]
        Game(kickoff=kickoff, deadline=deadline, round=self.rounds['vorrunde'],
             hometeam=hometeam, awayteam=awayteam, venue=self.venues[venue]).save()
