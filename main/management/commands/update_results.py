# -*- coding: utf-8 -*-
import logging

import requests

__author__ = 'mloeks'

from django.db.models import Q

from main.utils import get_reference_date, extract_goals_from_result
from main.models import Game

from django.core.management.base import BaseCommand

LOG = logging.getLogger('rtg.' + __name__)


class Command(BaseCommand):
    args = ''
    help = 'Check for new results on OpenLigaDB web service'

    def handle(self, *args, **options):
        for game in self.get_started_games_without_result():
            LOG.info('Looking for result of game %s (ID %s, OpenLigaDB ID %s)' %
                     (game, game.pk, game.openligadb_match_id))
            result = self.fetch_result_from_openligadb(game)
            if result:
                LOG.info('Setting result of game %s to %s' % (game, result))
                game.set_result_goals(*result)
                game.save()

    def get_started_games_without_result(self):
        return Game.objects\
            .filter(kickoff__lte=get_reference_date())\
            .filter(Q(homegoals=-1) | Q(awaygoals=-1))

    def fetch_result_from_openligadb(self, game):
        if not game.openligadb_match_id:
            LOG.warning('Cannot fetch result of game %s, OpenLigaDB ID is missing.' % game.pk)
            return None

        resp = requests\
            .get('https://www.openligadb.de/api/getmatchdata/%s' % game.openligadb_match_id)\
            .json()

        game_finished = resp['MatchIsFinished']
        results = resp['MatchResults']
        final_result = self.find_result_by_name(results, 'Endergebnis')
        result_after_90_mins = self.find_result_by_name(results, 'nach 90 Minuten')

        if not game.round.is_knock_out and game_finished and final_result:
            result = self.get_goals_from_match_result(final_result)
            LOG.info('Found result %s for non knock-out game %s' % (result, game))
            return result

        if game.round.is_knock_out and result_after_90_mins:
            result = self.get_goals_from_match_result(result_after_90_mins)
            LOG.info('Found result %s for knock-out game %s' % (result, game))
            return result

        LOG.info('No result found for game %s' % game)
        return None

    def find_result_by_name(self, result_list, result_name):
        matches = [res for res in result_list if res['ResultName'] == result_name]
        return matches[0] if matches else None

    def get_goals_from_match_result(self, match_result):
        return (match_result['PointsTeam1'], match_result['PointsTeam2'])
