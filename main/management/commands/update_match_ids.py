# -*- coding: utf-8 -*-
import logging

import dateutil
import requests
from django.db.models import Q

__author__ = 'mloeks'

from main.models import Game

from django.core.management.base import BaseCommand

LOG = logging.getLogger('rtg.' + __name__)


class Command(BaseCommand):
    args = ''
    help = 'Set OpenLigaDB match IDs on games'

    def handle(self, *args, **options):
        openligadb_games = self.fetch_games()
        for game in list(self.get_games_without_match_id()):
            match_found = False
            for ol_game in openligadb_games:
                if self.game_matches(game, ol_game):
                    LOG.info('Setting Match ID of game %s to %s' % (game, ol_game[0]))
                    match_found = True
                    game.openligadb_match_id = ol_game[0]
                    game.save()
                    break
            if not match_found:
                LOG.warning('No ID found for game %s (ID %s)' % (game, game.pk))

    def fetch_games(self):
        resp = requests.get('https://www.openligadb.de/api/getmatchdata/fifa18/2018').json()
        return [(
            g['MatchID'],
            dateutil.parser.parse(g['MatchDateTimeUTC']),
            g['Team1']['TeamName'],
            g['Team2']['TeamName']
        ) for g in resp]

    def get_games_without_match_id(self):
        return Game.objects\
            .filter(Q(openligadb_match_id__isnull=True) | Q(openligadb_match_id__exact=''))

    def game_matches(self, game, ol_game):
        return game.kickoff == ol_game[1] and game.hometeam.name.lower() == ol_game[2].lower() \
                    and game.awayteam.name.lower() == ol_game[3].lower()
