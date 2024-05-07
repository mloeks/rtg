# -*- coding: utf-8 -*-

from django.core.management.base import BaseCommand

from main.models import TournamentGroup, TournamentRound, Venue, Team, Game, Extra, ExtraChoice


class Command(BaseCommand):
    help = 'Creates the real EURO 2024 data'

    TOURNAMENT_START = '2024-06-14 21:00:00+02'

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
            'berlin': Venue(city='Berlin', name='Olympiastadion', capacity=70033),
            'dortmund': Venue(city='Dortmund', name='BVB Stadion', capacity=61524),
            'duesseldorf': Venue(city='Düsseldorf', name='Düsseldorf Arena', capacity=46264),
            'frankfurt': Venue(city='Frankfurt am Main', name='Frankfurt Arena', capacity=48057),
            'gelsenkirchen': Venue(city='Gelsenkirchen', name='Arena AufSchalke', capacity=49471),
            'hamburg': Venue(city='Hamburg', name='Volksparkstadion', capacity=50215),
            'koeln': Venue(city='Köln', name='Köln Stadion', capacity=46922),
            'leipzig': Venue(city='Leipzig', name='Leipzig Stadion', capacity=46635),
            'muenchen': Venue(city='München', name='München Arena', capacity=66026),
            'stuttgart': Venue(city='Stuttgart', name='Stuttgart Arena', capacity=50998),
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
            'GER': Team(name='Deutschland', abbreviation='GER', group=self.groups['a']),
            'SCO': Team(name='Schottland', abbreviation='SCO', group=self.groups['a']),
            'HUN': Team(name='Ungarn', abbreviation='HUN', group=self.groups['a']),
            'SUI': Team(name='Schweiz', abbreviation='SUI', group=self.groups['a']),

            'ESP': Team(name='Spanien', abbreviation='ESP', group=self.groups['b']),
            'CRO': Team(name='Kroatien', abbreviation='CRO', group=self.groups['b']),
            'ITA': Team(name='Italien', abbreviation='ITA', group=self.groups['b']),
            'ALB': Team(name='Albanien', abbreviation='ALB', group=self.groups['b']),

            'SVN': Team(name='Slowenien', abbreviation='SVN', group=self.groups['c']),
            'DEN': Team(name='Dänemark', abbreviation='DEN', group=self.groups['c']),
            'SRB': Team(name='Serbien', abbreviation='SRB', group=self.groups['c']),
            'ENG': Team(name='England', abbreviation='ENG', group=self.groups['c']),

            'POL': Team(name='Polen', abbreviation='POL', group=self.groups['d']),
            'NED': Team(name='Niederlande', abbreviation='NED', group=self.groups['d']),
            'AUT': Team(name='Österreich', abbreviation='AUT', group=self.groups['d']),
            'FRA': Team(name='Frankreich', abbreviation='FRA', group=self.groups['d']),

            'BEL': Team(name='Belgien', abbreviation='BEL', group=self.groups['e']),
            'SVK': Team(name='Slowakei', abbreviation='SVK', group=self.groups['e']),
            'ROU': Team(name='Rumänien', abbreviation='ROU', group=self.groups['e']),
            'UKR': Team(name='Ukraine', abbreviation='UKR', group=self.groups['e']),

            'TUR': Team(name='Türkei', abbreviation='TUR', group=self.groups['f']),
            'GEO': Team(name='Georgien', abbreviation='GEO', group=self.groups['f']),
            'POR': Team(name='Portugal', abbreviation='POR', group=self.groups['f']),
            'CZE': Team(name='Tschechien', abbreviation='CZE', group=self.groups['f']),
        }
        for key, team in teams.items():
            team.save()
        return teams

    def create_first_round_games(self):
        self.a_game('GER', 'SCO', self.TOURNAMENT_START, 'muenchen')
        self.a_game('HUN', 'SUI', '2024-06-15 15:00:00+02', 'koeln')
        self.a_game('ESP', 'CRO', '2024-06-15 18:00:00+02', 'berlin')
        self.a_game('ITA', 'ALB', '2024-06-15 21:00:00+02', 'dortmund')
        self.a_game('POL', 'NED', '2024-06-16 15:00:00+02', 'hamburg')
        self.a_game('SVN', 'DEN', '2024-06-16 18:00:00+02', 'stuttgart')
        self.a_game('SRB', 'ENG', '2024-06-16 21:00:00+02', 'gelsenkirchen')
        self.a_game('ROU', 'UKR', '2024-06-17 15:00:00+02', 'muenchen')
        self.a_game('BEL', 'SVK', '2024-06-17 18:00:00+02', 'frankfurt')
        self.a_game('AUT', 'FRA', '2024-06-17 21:00:00+02', 'duesseldorf')
        self.a_game('TUR', 'GEO', '2024-06-18 18:00:00+02', 'dortmund')
        self.a_game('POR', 'CZE', '2024-06-18 21:00:00+02', 'leipzig')

        self.a_game('CRO', 'ALB', '2024-06-19 15:00:00+02', 'hamburg')
        self.a_game('GER', 'HUN', '2024-06-19 18:00:00+02', 'stuttgart')
        self.a_game('SCO', 'SUI', '2024-06-19 21:00:00+02', 'koeln')
        self.a_game('SVN', 'SRB', '2024-06-20 15:00:00+02', 'muenchen')
        self.a_game('DEN', 'ENG', '2024-06-20 18:00:00+02', 'frankfurt')
        self.a_game('ESP', 'ITA', '2024-06-20 21:00:00+02', 'gelsenkirchen')
        self.a_game('SVK', 'UKR', '2024-06-21 15:00:00+02', 'duesseldorf')
        self.a_game('POL', 'AUT', '2024-06-21 18:00:00+02', 'berlin')
        self.a_game('NED', 'FRA', '2024-06-21 21:00:00+02', 'leipzig')
        self.a_game('GEO', 'CZE', '2024-06-22 15:00:00+02', 'hamburg')
        self.a_game('TUR', 'POR', '2024-06-22 18:00:00+02', 'dortmund')
        self.a_game('BEL', 'ROU', '2024-06-22 21:00:00+02', 'koeln')

        self.a_game('SUI', 'GER', '2024-06-23 21:00:00+02', 'frankfurt')
        self.a_game('SCO', 'HUN', '2024-06-23 21:00:00+02', 'stuttgart')
        self.a_game('CRO', 'ITA', '2024-06-24 21:00:00+02', 'leipzig')
        self.a_game('ALB', 'ESP', '2024-06-24 21:00:00+02', 'duesseldorf')
        self.a_game('NED', 'AUT', '2024-06-25 18:00:00+02', 'berlin')
        self.a_game('FRA', 'POL', '2024-06-25 18:00:00+02', 'dortmund')
        self.a_game('ENG', 'SVN', '2024-06-25 21:00:00+02', 'koeln')
        self.a_game('DEN', 'SRB', '2024-06-25 21:00:00+02', 'muenchen')
        self.a_game('SVK', 'ROU', '2024-06-26 18:00:00+02', 'frankfurt')
        self.a_game('UKR', 'BEL', '2024-06-26 18:00:00+02', 'stuttgart')
        self.a_game('GEO', 'POR', '2024-06-26 21:00:00+02', 'gelsenkirchen')
        self.a_game('CZE', 'TUR', '2024-06-26 21:00:00+02', 'hamburg')

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
