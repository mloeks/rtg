# -*- coding: utf-8 -*-

from django.core.management.base import BaseCommand

from main.models import TournamentGroup, TournamentRound, Venue, Team, Game, Extra, ExtraChoice


class Command(BaseCommand):
    help = 'Creates the real World Cup 2018 data'

    TOURNAMENT_START = '2018-06-14 17:00:00+02'

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
            'jekaterinburg': Venue(city='Jekaterinburg', name='Zentralstadion', capacity=35696),
            'kaliningrad': Venue(city='Kaliningrad', name='Kaliningrad-Stadion', capacity=35202),
            'kasan': Venue(city='Kasan', name='Kasan-Arena', capacity=45015),
            'nischni-nowgorod': Venue(city='Nischni Nowgorod', name='Stadion Nischni Nowgorod', capacity=44899),
            'moskau-spartak': Venue(city='Moskau (Spartak)', name='Spartak-Stadion', capacity=45360),
            'samara': Venue(city='Samara', name='Kosmos-Arena', capacity=44918),
            'wolgograd': Venue(city='Wolgograd', name='Wolgograd Arena', capacity=45015),
            'sankt-petersburg': Venue(city='Sankt Petersburg', name='Sankt-Petersburg-Stadion', capacity=68134),
            'sotschi': Venue(city='Sotschi', name='Olympiastadion', capacity=44000),
            'saransk': Venue(city='Saransk', name='Mordowia Arena', capacity=45015),
            'rostow': Venue(city='Rostow am Don', name='Rostow Arena', capacity=45000),
            'moskau-luschniki': Venue(city='Moskau (Luschniki)', name='Luschniki', capacity=81000),
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

    def create_teams(self):
        teams = {
            'EGY': Team(name='Ägypten', abbreviation='EGY', group=self.groups['a']),
            'RUS': Team(name='Russland', abbreviation='RUS', group=self.groups['a']),
            'KSA': Team(name='Saudi-Arabien', abbreviation='KSA', group=self.groups['a']),
            'URU': Team(name='Uruguay', abbreviation='URU', group=self.groups['a']),

            'IRN': Team(name='Iran', abbreviation='IRN', group=self.groups['b']),
            'MAR': Team(name='Marokko', abbreviation='MAR', group=self.groups['b']),
            'POR': Team(name='Portugal', abbreviation='POR', group=self.groups['b']),
            'ESP': Team(name='Spanien', abbreviation='ESP', group=self.groups['b']),

            'AUS': Team(name='Australien', abbreviation='AUS', group=self.groups['c']),
            'DEN': Team(name='Dänemark', abbreviation='DEN', group=self.groups['c']),
            'FRA': Team(name='Frankreich', abbreviation='FRA', group=self.groups['c']),
            'PER': Team(name='Peru', abbreviation='PER', group=self.groups['c']),

            'ARG': Team(name='Argentinien', abbreviation='ARG', group=self.groups['d']),
            'ISL': Team(name='Island', abbreviation='ISL', group=self.groups['d']),
            'CRO': Team(name='Kroatien', abbreviation='CRO', group=self.groups['d']),
            'NGA': Team(name='Nigeria', abbreviation='NGA', group=self.groups['d']),

            'BRA': Team(name='Brasilien', abbreviation='BRA', group=self.groups['e']),
            'CRC': Team(name='Costa Rica', abbreviation='CRC', group=self.groups['e']),
            'SUI': Team(name='Schweiz', abbreviation='SUI', group=self.groups['e']),
            'SRB': Team(name='Serbien', abbreviation='SRB', group=self.groups['e']),

            'GER': Team(name='Deutschland', abbreviation='GER', group=self.groups['f']),
            'MEX': Team(name='Mexiko', abbreviation='MEX', group=self.groups['f']),
            'SWE': Team(name='Schweden', abbreviation='SWE', group=self.groups['f']),
            'KOR': Team(name='Südkorea', abbreviation='KOR', group=self.groups['f']),

            'BEL': Team(name='Belgien', abbreviation='BEL', group=self.groups['g']),
            'ENG': Team(name='England', abbreviation='ENG', group=self.groups['g']),
            'PAN': Team(name='Panama', abbreviation='PAN', group=self.groups['g']),
            'TUN': Team(name='Tunesien', abbreviation='TUN', group=self.groups['g']),

            'JPN': Team(name='Japan', abbreviation='JPN', group=self.groups['h']),
            'COL': Team(name='Kolumbien', abbreviation='COL', group=self.groups['h']),
            'POL': Team(name='Polen', abbreviation='POL', group=self.groups['h']),
            'SEN': Team(name='Senegal', abbreviation='SEN', group=self.groups['h']),
        }

        for key, team in teams.items():
            team.save()
        return teams

    def create_first_round_games(self):
        self.a_game('RUS', 'KSA', self.TOURNAMENT_START, 'moskau-luschniki')
        self.a_game('EGY', 'URU', '2018-06-15 14:00:00+02', 'jekaterinburg')
        self.a_game('MAR', 'IRN', '2018-06-15 17:00:00+02', 'sankt-petersburg')
        self.a_game('POR', 'ESP', '2018-06-15 20:00:00+02', 'sotschi')
        self.a_game('FRA', 'AUS', '2018-06-16 12:00:00+02', 'kasan')
        self.a_game('ARG', 'ISL', '2018-06-16 15:00:00+02', 'moskau-spartak')
        self.a_game('PER', 'DEN', '2018-06-16 18:00:00+02', 'saransk')
        self.a_game('CRO', 'NGA', '2018-06-16 21:00:00+02', 'kaliningrad')
        self.a_game('CRC', 'SRB', '2018-06-17 14:00:00+02', 'samara')
        self.a_game('GER', 'MEX', '2018-06-17 17:00:00+02', 'moskau-luschniki')
        self.a_game('BRA', 'SUI', '2018-06-17 20:00:00+02', 'rostow')
        self.a_game('SWE', 'KOR', '2018-06-18 14:00:00+02', 'nischni-nowgorod')
        self.a_game('BEL', 'PAN', '2018-06-18 17:00:00+02', 'sotschi')
        self.a_game('TUN', 'ENG', '2018-06-18 20:00:00+02', 'wolgograd')
        self.a_game('COL', 'JPN', '2018-06-19 14:00:00+02', 'saransk')
        self.a_game('POL', 'SEN', '2018-06-19 17:00:00+02', 'moskau-spartak')

        self.a_game('RUS', 'EGY', '2018-06-19 20:00:00+02', 'sankt-petersburg')
        self.a_game('POR', 'MAR', '2018-06-20 14:00:00+02', 'moskau-luschniki')
        self.a_game('URU', 'KSA', '2018-06-20 17:00:00+02', 'rostow')
        self.a_game('IRN', 'ESP', '2018-06-20 20:00:00+02', 'kasan')
        self.a_game('DEN', 'AUS', '2018-06-21 14:00:00+02', 'samara')
        self.a_game('FRA', 'PER', '2018-06-21 17:00:00+02', 'jekaterinburg')
        self.a_game('ARG', 'CRO', '2018-06-21 20:00:00+02', 'nischni-nowgorod')
        self.a_game('BRA', 'CRC', '2018-06-22 14:00:00+02', 'sankt-petersburg')
        self.a_game('NGA', 'ISL', '2018-06-22 17:00:00+02', 'wolgograd')
        self.a_game('SRB', 'SUI', '2018-06-22 20:00:00+02', 'kaliningrad')
        self.a_game('BEL', 'TUN', '2018-06-23 14:00:00+02', 'moskau-spartak')
        self.a_game('KOR', 'MEX', '2018-06-23 17:00:00+02', 'rostow')
        self.a_game('GER', 'SWE', '2018-06-23 20:00:00+02', 'sotschi')
        self.a_game('ENG', 'PAN', '2018-06-24 14:00:00+02', 'nischni-nowgorod')
        self.a_game('JPN', 'SEN', '2018-06-24 17:00:00+02', 'jekaterinburg')
        self.a_game('POL', 'COL', '2018-06-24 20:00:00+02', 'kasan')

        self.a_game('URU', 'RUS', '2018-06-25 16:00:00+02', 'samara')
        self.a_game('KSA', 'EGY', '2018-06-25 16:00:00+02', 'wolgograd')
        self.a_game('ESP', 'MAR', '2018-06-25 20:00:00+02', 'kaliningrad')
        self.a_game('IRN', 'POR', '2018-06-25 20:00:00+02', 'saransk')
        self.a_game('DEN', 'FRA', '2018-06-26 16:00:00+02', 'moskau-luschniki')
        self.a_game('AUS', 'PER', '2018-06-26 16:00:00+02', 'sotschi')
        self.a_game('ISL', 'CRO', '2018-06-26 20:00:00+02', 'rostow')
        self.a_game('NGA', 'ARG', '2018-06-26 20:00:00+02', 'sankt-petersburg')
        self.a_game('MEX', 'SWE', '2018-06-27 16:00:00+02', 'jekaterinburg')
        self.a_game('KOR', 'GER', '2018-06-27 16:00:00+02', 'kasan')
        self.a_game('SRB', 'BRA', '2018-06-27 20:00:00+02', 'moskau-spartak')
        self.a_game('SUI', 'CRC', '2018-06-27 20:00:00+02', 'nischni-nowgorod')
        self.a_game('SEN', 'COL', '2018-06-28 16:00:00+02', 'samara')
        self.a_game('JPN', 'POL', '2018-06-28 16:00:00+02', 'wolgograd')
        self.a_game('ENG', 'BEL', '2018-06-28 20:00:00+02', 'kaliningrad')
        self.a_game('PAN', 'TUN', '2018-06-28 20:00:00+02', 'saransk')

    def create_extra_bets(self):
        wm = Extra(name='Wer wird Weltmeister?', points=5, deadline=self.TOURNAMENT_START)
        deu = Extra(name='Wie weit kommt Deutschland?', points=5, deadline=self.TOURNAMENT_START)
        wm.save()
        deu.save()

        for team in Team.objects.all():
            ExtraChoice(name=team.name, extra=wm, sort_index=team.name[0:9]).save()

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
