# -*- coding: utf-8 -*-

from django.core.management.base import BaseCommand

from main.models import TournamentGroup, TournamentRound, Venue, Team, Game, Extra, ExtraChoice


class Command(BaseCommand):
    help = 'Creates the real EURO 2020 data'

    TOURNAMENT_START = '2021-06-11 21:00:00+02'

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
            'london': Venue(city='London', name='Wembley Stadium', capacity=90000),
            'baku': Venue(city='Baku', name='Nationalstadion', capacity=68700),
            'muenchen': Venue(city='München', name='Allianz Arena', capacity=70000),
            'glasgow': Venue(city='Glasgow', name='Hampden Park', capacity=51866),
            'sevilla': Venue(city='Sevilla', name='La Cartuja', capacity=60000),
            'amsterdam': Venue(city='Amsterdam', name='Johan-Cruyff-Arena', capacity=54990),
            'budapest': Venue(city='Budapest', name='Puskás Aréna', capacity=67215),
            'bukarest': Venue(city='Bukarest', name='Arena Nationala', capacity=55600),
            'kopenhagen': Venue(city='Kopenhagen', name='Parken', capacity=38065),
            'sankt-petersburg': Venue(city='Sankt Petersburg', name='Krestowski-Stadion', capacity=68134),
            'rom': Venue(city='Rom', name='Olimpico', capacity=70634),
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

    # Country codes according to official FIFA code list
    # See https://de.wikipedia.org/wiki/FIFA-L%C3%A4ndercode
    def create_teams(self):
        teams = {
            'ITA': Team(name='Italien', abbreviation='ITA', group=self.groups['a']),
            'SUI': Team(name='Schweiz', abbreviation='SUI', group=self.groups['a']),
            'TUR': Team(name='Türkei', abbreviation='TUR', group=self.groups['a']),
            'WAL': Team(name='Wales', abbreviation='WAL', group=self.groups['a']),

            'BEL': Team(name='Belgien', abbreviation='BEL', group=self.groups['b']),
            'DEN': Team(name='Dänemark', abbreviation='DEN', group=self.groups['b']),
            'FIN': Team(name='Finnland', abbreviation='FIN', group=self.groups['b']),
            'RUS': Team(name='Russland', abbreviation='RUS', group=self.groups['b']),

            'NED': Team(name='Niederlande', abbreviation='NED', group=self.groups['c']),
            'MKD': Team(name='Nordmazedonien', abbreviation='MKD', group=self.groups['c']),
            'AUT': Team(name='Österreich', abbreviation='AUT', group=self.groups['c']),
            'UKR': Team(name='Ukraine', abbreviation='UKR', group=self.groups['c']),

            'ENG': Team(name='England', abbreviation='ENG', group=self.groups['d']),
            'CRO': Team(name='Kroatien', abbreviation='CRO', group=self.groups['d']),
            'SCO': Team(name='Schottland', abbreviation='SCO', group=self.groups['d']),
            'CZE': Team(name='Tschechien', abbreviation='CZE', group=self.groups['d']),

            'POL': Team(name='Polen', abbreviation='POL', group=self.groups['e']),
            'SWE': Team(name='Schweden', abbreviation='SWE', group=self.groups['e']),
            'SVK': Team(name='Slowakei', abbreviation='SVK', group=self.groups['e']),
            'ESP': Team(name='Spanien', abbreviation='ESP', group=self.groups['e']),

            'GER': Team(name='Deutschland', abbreviation='GER', group=self.groups['f']),
            'FRA': Team(name='Frankreich', abbreviation='FRA', group=self.groups['f']),
            'POR': Team(name='Portugal', abbreviation='POR', group=self.groups['f']),
            'HUN': Team(name='Ungarn', abbreviation='HUN', group=self.groups['f']),
        }

        for key, team in teams.items():
            team.save()
        return teams

    def create_first_round_games(self):
        self.a_game('TUR', 'ITA', self.TOURNAMENT_START, 'rom')
        self.a_game('WAL', 'SUI', '2021-06-12 15:00:00+02', 'baku')
        self.a_game('DEN', 'FIN', '2021-06-12 18:00:00+02', 'kopenhagen')
        self.a_game('BEL', 'RUS', '2021-06-12 21:00:00+02', 'sankt-petersburg')
        self.a_game('ENG', 'CRO', '2021-06-13 15:00:00+02', 'london')
        self.a_game('AUT', 'MKD', '2021-06-13 18:00:00+02', 'bukarest')
        self.a_game('NED', 'UKR', '2021-06-13 21:00:00+02', 'amsterdam')
        self.a_game('SCO', 'CZE', '2021-06-14 15:00:00+02', 'glasgow')
        self.a_game('POL', 'SVK', '2021-06-14 18:00:00+02', 'sankt-petersburg')
        self.a_game('ESP', 'SWE', '2021-06-14 21:00:00+02', 'sevilla')
        self.a_game('HUN', 'POR', '2021-06-15 18:00:00+02', 'budapest')
        self.a_game('FRA', 'GER', '2021-06-15 21:00:00+02', 'muenchen')

        self.a_game('FIN', 'RUS', '2021-06-16 15:00:00+02', 'sankt-petersburg')
        self.a_game('TUR', 'WAL', '2021-06-16 18:00:00+02', 'baku')
        self.a_game('ITA', 'SUI', '2021-06-16 21:00:00+02', 'rom')
        self.a_game('UKR', 'MKD', '2021-06-17 15:00:00+02', 'bukarest')
        self.a_game('DEN', 'BEL', '2021-06-17 18:00:00+02', 'kopenhagen')
        self.a_game('NED', 'AUT', '2021-06-17 21:00:00+02', 'amsterdam')        
        self.a_game('SWE', 'SVK', '2021-06-18 15:00:00+02', 'sankt-petersburg')
        self.a_game('CRO', 'CZE', '2021-06-18 18:00:00+02', 'glasgow')
        self.a_game('ENG', 'SCO', '2021-06-18 21:00:00+02', 'london')
        self.a_game('HUN', 'FRA', '2021-06-19 15:00:00+02', 'budapest')
        self.a_game('POR', 'GER', '2021-06-19 18:00:00+02', 'muenchen')
        self.a_game('ESP', 'POL', '2021-06-19 21:00:00+02', 'sevilla')

        self.a_game('SUI', 'TUR', '2021-06-20 18:00:00+02', 'baku')
        self.a_game('ITA', 'WAL', '2021-06-20 18:00:00+02', 'rom')
        self.a_game('MKD', 'NED', '2021-06-21 18:00:00+02', 'amsterdam')
        self.a_game('UKR', 'AUT', '2021-06-21 18:00:00+02', 'bukarest')
        self.a_game('RUS', 'DEN', '2021-06-21 21:00:00+02', 'kopenhagen')
        self.a_game('FIN', 'BEL', '2021-06-21 21:00:00+02', 'sankt-petersburg')
        self.a_game('CRO', 'SCO', '2021-06-22 21:00:00+02', 'glasgow')
        self.a_game('CZE', 'ENG', '2021-06-22 21:00:00+02', 'london')
        self.a_game('SVK', 'ESP', '2021-06-23 18:00:00+02', 'sevilla')
        self.a_game('SWE', 'POL', '2021-06-23 18:00:00+02', 'sankt-petersburg')
        self.a_game('POR', 'FRA', '2021-06-23 21:00:00+02', 'budapest')
        self.a_game('GER', 'HUN', '2021-06-23 21:00:00+02', 'muenchen')

    def create_extra_bets(self):
        em = Extra(name='Wer wird Europameister?', points=5, deadline=self.TOURNAMENT_START)
        deu = Extra(name='Wie weit kommt Deutschland?', points=5, deadline=self.TOURNAMENT_START)
        em.save()
        deu.save()

        for team in Team.objects.all():
            ExtraChoice(name=team.name, extra=em, sort_index=team.name[0:9]).save()

        ExtraChoice(name='Vorrunde', extra=deu, sort_index='010').save()
        ExtraChoice(name='Achtelfinale', extra=deu, sort_index='020').save()
        ExtraChoice(name='Viertelfinale', extra=deu, sort_index='030').save()
        ExtraChoice(name='Halbfinale', extra=deu, sort_index='040').save()
        ExtraChoice(name='Zweiter', extra=deu, sort_index='050').save()
        ExtraChoice(name='Europameister', extra=deu, sort_index='060').save()

    def a_game(self, home, away, kickoff, venue, deadline=TOURNAMENT_START):
        hometeam = self.teams[home]
        awayteam = self.teams[away]
        Game(kickoff=kickoff, deadline=deadline, round=self.rounds['vorrunde'],
             hometeam=hometeam, awayteam=awayteam, venue=self.venues[venue]).save()
