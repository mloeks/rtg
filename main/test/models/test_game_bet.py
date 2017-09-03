# -*- coding: utf-8 -*-

from django.db import transaction
from django.db.utils import IntegrityError
from django.test import TestCase

from main.models import Game, GameBet, GameBetResult
from main.test.utils import TestModelUtils as utils


class GameBetTests(TestCase):

    def tearDown(self):
        Game.objects.all().delete()
        GameBet.objects.all().delete()
        utils.cleanup()

    def test_to_string(self):
        g1, g2, u = utils.create_game(), utils.create_game(), utils.create_user()
        GameBet.objects.create(homegoals=4, awaygoals=2, game=g1, user=u)
        gamebet = GameBet.objects.get(user=u, game=g1)
        self.assertEqual('4:2', str(gamebet))

        GameBet.objects.create(game=g2, user=u)
        gamebet = GameBet.objects.get(user=u, game=g2)
        self.assertEqual('-:-', str(gamebet))

    def test_invalid_missing_fields(self):
        g, u = utils.create_game(), utils.create_user()
        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                GameBet.objects.create(game=g, user=None)
        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                GameBet.objects.create(game=None, user=u)

    def test_invalid_duplicates(self):
        g1, g2, u1, u2 = utils.create_game(), utils.create_game(), utils.create_user(), utils.create_user()
        GameBet.objects.create(game=g1, user=u1)
        GameBet.objects.create(game=g2, user=u2)
        GameBet.objects.create(game=g1, user=u2)
        GameBet.objects.create(game=g2, user=u1)
        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                GameBet.objects.create(game=g1, user=u2)

    def test_has_bet(self):
        u, g = utils.create_user(), utils.create_game()

        gb = GameBet.objects.create(game=g, user=u)
        self.assertFalse(gb.has_bet())

        gb.homegoals = 3
        self.assertFalse(gb.has_bet())

        gb.awaygoals = 5
        gb.homegoals = -1
        self.assertFalse(gb.has_bet())

        gb.homegoals = 3
        self.assertTrue(gb.has_bet())

    def test_has_result(self):
        utils.create_gamebet_result_types()
        u, g = utils.create_user(), utils.create_game()

        gb = GameBet.objects.create(game=g, user=u)
        self.assertFalse(gb.has_result())

        gb.delete()
        gb = GameBet.objects.create(game=g, user=u, result_bet_type=GameBetResult.objects.get(type='volltreffer'))
        self.assertTrue(gb.has_result())

    def test_get_user_bets(self):
        u1, u2, u3 = utils.create_user(), utils.create_user(), utils.create_user()

        u1_bets = [utils.create_gamebet(u1) for i in range(1, 5)]
        u2_bets = [utils.create_gamebet(u2) for i in range(1, 3)]
        u3_bets = [utils.create_gamebet(u3) for i in range(1, 8)]

        self.assertEqual(13, len(GameBet.objects.all()))
        self.assertListEqual(u1_bets, list(GameBet.get_user_bets(u1.pk)))
        self.assertListEqual(u2_bets, list(GameBet.get_user_bets(u2.pk)))
        self.assertListEqual(u3_bets, list(GameBet.get_user_bets(u3.pk)))

    def test_get_user_bets_finished(self):
        utils.create_gamebet_result_types()
        u1, u2 = utils.create_user(), utils.create_user()
        g1, g2, g3 = utils.create_game(homegoals=3, awaygoals=2), \
                     utils.create_game(), \
                     utils.create_game(homegoals=0, awaygoals=0)

        gb1 = utils.create_gamebet(u1, g1, 2, 1)
        gb2 = utils.create_gamebet(u1, g2, 2, 1)
        gb3 = utils.create_gamebet(u1, g3)
        gb4 = utils.create_gamebet(u2, g1, 0, 0)
        gb5 = utils.create_gamebet(u2, g2, 0, 3)
        gb6 = utils.create_gamebet(u2, g3, 2, 2)

        [gb.save() for gb in [gb1, gb2, gb3, gb4, gb5, gb6]]
        [g.save() for g in [g1, g2, g3]]

        self.assertEqual(6, len(GameBet.objects.all()))
        self.assertListEqual([gb1], list(GameBet.get_user_bets(u1.pk, True)))
        self.assertListEqual([gb4, gb6], list(GameBet.get_user_bets(u2.pk, True)))

    def test_get_game_bets(self):
        g1, g2, g3 = utils.create_game(), utils.create_game(), utils.create_game()

        g1_bets = [utils.create_gamebet(game=g1) for i in range(1, 2)]
        g2_bets = [utils.create_gamebet(game=g2) for i in range(1, 5)]
        g3_bets = [utils.create_gamebet(game=g3) for i in range(1, 7)]

        self.assertEqual(11, len(GameBet.objects.all()))
        self.assertListEqual(g1_bets, list(GameBet.get_game_bets(g1.pk)))
        self.assertListEqual(g2_bets, list(GameBet.get_game_bets(g2.pk)))
        self.assertListEqual(g3_bets, list(GameBet.get_game_bets(g3.pk)))

    def test_get_game_bets_finished(self):
        utils.create_gamebet_result_types()
        u1, u2 = utils.create_user(), utils.create_user()
        g1, g2, g3 = utils.create_game(homegoals=1, awaygoals=2), \
                     utils.create_game(), \
                     utils.create_game(homegoals=3, awaygoals=0)

        gb1 = utils.create_gamebet(u1, g1, 2, 1)
        gb2 = utils.create_gamebet(u1, g2, 2, 1)
        gb3 = utils.create_gamebet(u1, g3)
        gb4 = utils.create_gamebet(u2, g1, 0, 0)
        gb5 = utils.create_gamebet(u2, g2, 0, 3)
        gb6 = utils.create_gamebet(u2, g3, 2, 2)

        [gb.save() for gb in [gb1, gb2, gb3, gb4, gb5, gb6]]
        [g.save() for g in [g1, g2, g3]]

        self.assertEqual(6, len(GameBet.objects.all()))
        self.assertListEqual([gb1, gb4], list(GameBet.get_game_bets(g1.pk, True)))
        self.assertListEqual([], list(GameBet.get_game_bets(g2.pk, True)))
        self.assertListEqual([gb6], list(GameBet.get_game_bets(g3.pk, True)))

    def test_get_user_game_bet(self):
        u1, u2 = utils.create_user(), utils.create_user()
        g1, g2 = utils.create_game(), utils.create_game()

        gb1 = utils.create_gamebet(u1, g1)
        gb2 = utils.create_gamebet(u1, g2)
        gb3 = utils.create_gamebet(u2, g1)

        self.assertEqual(gb1, GameBet.get_user_game_bet(u1.pk, g1.pk))
        self.assertEqual(gb2, GameBet.get_user_game_bet(u1.pk, g2.pk))
        self.assertEqual(gb3, GameBet.get_user_game_bet(u2.pk, g1.pk))
        self.assertIsNone(GameBet.get_user_game_bet(u2.pk, g2.pk))

    def test_compute_gamebet_result_type_none(self):
        u, g, g_r = utils.create_user(), utils.create_game(), utils.create_game(homegoals=3, awaygoals=1)

        # game has no result
        gb1 = utils.create_gamebet(u, g, homegoals=3, awaygoals=1)
        gb1.compute_gamebet_result_type()
        self.assertIsNone(gb1.result_bet_type)

        # no bet was set
        gb2 = utils.create_gamebet(u, g_r)
        gb2.compute_gamebet_result_type()
        self.assertIsNone(gb2.result_bet_type)

    def test_compute_gamebet_result_type_volltreffer(self):
        utils.create_gamebet_result_types()
        u, g, g_r = utils.create_user(), utils.create_game(homegoals=3, awaygoals=1), \
                    utils.create_game(homegoals=1, awaygoals=1)

        gb = utils.create_gamebet(u, g, homegoals=3, awaygoals=1)
        gb.compute_gamebet_result_type()
        self.assertEqual('volltreffer', gb.result_bet_type.type)

        gb = utils.create_gamebet(u, g_r, homegoals=1, awaygoals=1)
        gb.compute_gamebet_result_type()
        self.assertEqual('volltreffer', gb.result_bet_type.type)

    def test_compute_gamebet_result_type_differenz(self):
        utils.create_gamebet_result_types()
        u, g = utils.create_user(), utils.create_game(homegoals=4, awaygoals=0)

        gb = utils.create_gamebet(u, g, homegoals=6, awaygoals=2)
        gb.compute_gamebet_result_type()
        self.assertEqual('differenz', gb.result_bet_type.type)

    def test_compute_gamebet_result_type_remis_tendenz(self):
        utils.create_gamebet_result_types()
        u, g = utils.create_user(), utils.create_game(homegoals=1, awaygoals=1)

        gb = utils.create_gamebet(u, g, homegoals=3, awaygoals=3)
        gb.compute_gamebet_result_type()
        self.assertEqual('remis-tendenz', gb.result_bet_type.type)

    def test_compute_gamebet_result_type_tendenz(self):
        utils.create_gamebet_result_types()
        u, g = utils.create_user(), utils.create_game(homegoals=2, awaygoals=0)

        gb = utils.create_gamebet(u, g, homegoals=3, awaygoals=0)
        gb.compute_gamebet_result_type()
        self.assertEqual('tendenz', gb.result_bet_type.type)

        GameBet.objects.all().delete()

        gb = utils.create_gamebet(u, g, homegoals=3, awaygoals=2)
        gb.compute_gamebet_result_type()
        self.assertEqual('tendenz', gb.result_bet_type.type)

    def test_compute_gamebet_result_type_niete(self):
        utils.create_gamebet_result_types()
        u, g, g_r = utils.create_user(), utils.create_game(homegoals=2, awaygoals=1), \
                    utils.create_game(homegoals=0, awaygoals=0)

        gb = utils.create_gamebet(u, g, homegoals=0, awaygoals=1)
        gb.compute_gamebet_result_type()
        self.assertEqual('niete', gb.result_bet_type.type)

        gb = utils.create_gamebet(u, g_r, homegoals=1, awaygoals=2)
        gb.compute_gamebet_result_type()
        self.assertEqual('niete', gb.result_bet_type.type)