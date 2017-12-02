# -*- coding: utf-8 -*-
from django.test import TestCase

from main.models import Bet, Game, Bettable
from main.test.utils import TestModelUtils


class GameResultBetUpdateTests(TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        Bettable.objects.all().delete()
        Game.objects.all().delete()
        Bet.objects.all().delete()

    def test_new_game_result_updates_bettable(self):
        # GIVEN: some game
        some_game = TestModelUtils.create_game()

        # WHEN: the game gets a result
        some_game.homegoals = 3
        some_game.awaygoals = 1
        some_game.save()

        # THEN: the parent bettable should have this result set
        self.assertEqual('3:1', Bettable.objects.get(pk=some_game.pk).result)

    def test_new_game_result_updates_bet(self):
        # GIVEN: some game
        some_game = TestModelUtils.create_game()

        # AND: some bet
        some_bet = TestModelUtils.create_bet(bettable=some_game, result_bet="2:0")

        # WHEN: the game gets a result
        some_game.homegoals = 3
        some_game.awaygoals = 1
        some_game.save()

        # THEN: the bet should have the correct points
        updated_bet = Bet.objects.get(pk=some_bet.pk)
        self.assertEqual(3, updated_bet.points)
        self.assertEqual('differenz', updated_bet.result_bet_type)

    # TODO why is this test green? I would expect it to be red.
    def test_remove_game_result_resets_bettable(self):
        # GIVEN: some game with a result
        some_game = TestModelUtils.create_game(homegoals=3, awaygoals=2)

        # THEN: the bettable should have the result set
        self.assertEquals("3:2", Bettable.objects.get(pk=some_game.pk).result)

        # WHEN: the game's result is reset
        some_game.homegoals = -1
        some_game.awaygoals = -1
        some_game.save()

        # THEN: the bettable's result should be None
        self.assertIsNone(Bettable.objects.get(pk=some_game.pk).result)

    def test_remove_game_result_resets_bet_points(self):
        # GIVEN: some game with a result
        some_game = TestModelUtils.create_game(homegoals=3, awaygoals=2)

        # AND: some bet with points
        some_bet = TestModelUtils.create_bet(bettable=some_game, result_bet="2:0")
        some_bet.points = 4711
        some_bet.save()

        # WHEN: the game's result is reset
        some_game.homegoals = -1
        some_game.awaygoals = -1
        some_game.save()

        # THEN: the bet should reset it's points
        updated_bet = Bet.objects.get(pk=some_bet.pk)
        self.assertIsNone(updated_bet.points)
