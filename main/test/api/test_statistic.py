# -*- coding: utf-8 -*-

from django.contrib.auth.models import User
from rest_framework import status

from main.models import Game, Bet, Statistic
from main.test.api.abstract_rtg_api_test import RtgApiTestCase
from test.utils import TestModelUtils


class StatisticApiTests(RtgApiTestCase):
    user = None
    game = None
    bet = None

    def setUp(self):
        self.user = self.create_test_user('user', True, True)
        self.game = TestModelUtils.create_game()
        self.bet = TestModelUtils.create_bet(self.user, self.game, '2:1')

    def tearDown(self):
        User.objects.all().delete()
        Game.objects.all().delete()
        Bet.objects.all().delete()
        Statistic.objects.all().delete()

    def test_recalculate_after_game_update(self):
        response = self.client.patch("%s%i/" % (self.GAMES_BASEURL, self.game.pk), {'homegoals': 3, 'awaygoals': 2},
                                     format='json')
        self.assertEqual(status.HTTP_200_OK, response.status_code)

        updated_bet = self.client.get("%s%i/" % (self.BETS_BASEURL, self.bet.pk)).data
        self.assertEqual(3, updated_bet['points'])

        user_stats = self.client.get("%s%i/" % (self.STATISTICS_BASEURL, self.user.pk)).data
        self.assertEqual(3, user_stats['points'])
        self.assertEqual(1, user_stats['no_differenz'])
        self.assertEqual(1, user_stats['no_bets'])
