# -*- coding: utf-8 -*-
from django.test import TestCase

from main.models import Bet, Game
from main.test.utils import TestModelUtils


class GameResultBetUpdateTests(TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        Game.objects.all().delete()
        Bet.objects.all().delete()

    def test_new_game_result_updates_bet(self):
        # GIVEN: some game
        some_game = TestModelUtils.create_game()

        # AND: some bet
        some_bet = TestModelUtils.create_bet(game=some_game, homegoals=2, awaygoals=0)

        # WHEN: the game gets a result
        some_game.homegoals = 3
        some_game.awaygoals = 1
        some_game.save()

        # THEN: the bet should have the correct points
        updated_bet = Bet.objects.get(pk=some_bet.pk)
        print(updated_bet)
        self.assertEqual(5, updated_bet.points)
        self.assertEqual('differenz', updated_bet.result_bet_type)
