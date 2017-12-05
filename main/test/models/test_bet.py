# -*- coding: utf-8 -*-
from random import randrange

from django.db import transaction
from django.db.utils import IntegrityError
from django.test import TestCase

from main.models import Game, Bet, Team, Bettable
from main.test.utils import TestModelUtils as utils


class BetTests(TestCase):

    def tearDown(self):
        Bettable.objects.all().delete()
        Game.objects.all().delete()
        Bet.objects.all().delete()
        Team.objects.all().delete()
        utils.cleanup()

    def test_to_string(self):
        g1, g2, u = utils.create_game(), utils.create_game(), utils.create_user()
        utils.create_bet(result_bet="4:2", bettable=g1, user=u)
        bet = Bet.objects.get(user=u, bettable=g1)
        self.assertEqual('4:2', str(bet))

        utils.create_bet(bettable=g2, user=u)
        bet = Bet.objects.get(user=u, bettable=g2)
        self.assertEqual('---', str(bet))

    def test_invalid_missing_fields(self):
        g, u = utils.create_game(), utils.create_user()
        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                Bet.objects.create(bettable=g, user=None)
        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                Bet.objects.create(bettable=None, user=u)

    def test_invalid_duplicates(self):
        g1, g2, u1, u2 = utils.create_game(), utils.create_game(), utils.create_user(), utils.create_user()
        utils.create_bet(bettable=g1, user=u1)
        utils.create_bet(bettable=g2, user=u2)
        utils.create_bet(bettable=g1, user=u2)
        utils.create_bet(bettable=g2, user=u1)
        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                utils.create_bet(bettable=g1, user=u2)

    def test_has_bet(self):
        u, g = utils.create_user(), utils.create_game()

        gb = utils.create_bet(user=u, bettable=g)
        self.assertFalse(gb.has_bet())

        gb.result_bet = ''
        self.assertFalse(gb.has_bet())

        gb.result_bet = 'some_result_bet'
        self.assertTrue(gb.has_bet())

    def test_get_bets_by_user(self):
        u1, u2, u3 = utils.create_user(), utils.create_user(), utils.create_user()

        u1_bets = [utils.create_bet(u1) for i in range(4)]
        u2_bets = [utils.create_bet(u2) for i in range(2)]
        u3_bets = [utils.create_bet(u3) for i in range(7)]

        self.assertEqual(13, len(Bet.objects.all()))
        self.assertItemsEqual(u1_bets, list(Bet.get_by_user(u1.pk)))
        self.assertItemsEqual(u2_bets, list(Bet.get_by_user(u2.pk)))
        self.assertItemsEqual(u3_bets, list(Bet.get_by_user(u3.pk)))

    def test_get_bets_by_user_and_has_bet_and_bettable_has_result(self):
        u1, u2 = utils.create_user(), utils.create_user()
        g1, g2, g3 = utils.create_game(name="g1", homegoals=3, awaygoals=2), \
                     utils.create_game(name="g2"), \
                     utils.create_game(name="g3", homegoals=0, awaygoals=0)

        bet1 = utils.create_bet(u1, g1, "2:1")
        bet2 = utils.create_bet(u1, g2, "2:1")
        bet3 = utils.create_bet(u1, g3)
        bet4 = utils.create_bet(u2, g1, "0:0")
        bet5 = utils.create_bet(u2, g2, "0:3")
        bet6 = utils.create_bet(u2, g3, "2:2")

        [gb.save() for gb in [bet1, bet2, bet3, bet4, bet5, bet6]]
        [g.save() for g in [g1, g2, g3]]

        self.assertEqual(6, len(Bet.objects.all()))
        self.assertItemsEqual([bet1], list(Bet.get_by_user_and_has_bet_and_bettable_has_result(u1.pk)))
        self.assertItemsEqual([bet4, bet6], list(Bet.get_by_user_and_has_bet_and_bettable_has_result(u2.pk)))

    def test_get_bets_by_bettable(self):
        g1, g2 = utils.create_game(), utils.create_game()

        g1_bets = [utils.create_bet(bettable=g1, result_bet="%s:%s" % (randrange(5), randrange(5)))]
        g2_bets = [utils.create_bet(bettable=g2, result_bet="%s:%s" % (randrange(5), randrange(5))) for i in range(4)]

        self.assertEqual(5, len(Bet.objects.all()))
        self.assertItemsEqual(g1_bets, list(Bet.get_by_bettable(g1.pk)))
        self.assertItemsEqual(g2_bets, list(Bet.get_by_bettable(g2.pk)))

    def test_get_bets_by_bettable_and_bettable_has_result(self):
        u1, u2 = utils.create_user(), utils.create_user()
        g1, g2, g3 = utils.create_game(name="g1", homegoals=1, awaygoals=2), \
                     utils.create_game(name="g2"), \
                     utils.create_game(name="g3", homegoals=3, awaygoals=0)

        bet1 = utils.create_bet(u1, g1, "2:1")
        bet2 = utils.create_bet(u1, g2, "2:1")
        bet3 = utils.create_bet(u1, g3)
        bet4 = utils.create_bet(u2, g1, "0:0")
        bet5 = utils.create_bet(u2, g2, "0:3")
        bet6 = utils.create_bet(u2, g3, "2:2")

        [gb.save() for gb in [bet1, bet2, bet3, bet4, bet5, bet6]]
        [g.save() for g in [g1, g2, g3]]

        self.assertEqual(6, len(Bet.objects.all()))
        self.assertItemsEqual([bet4, bet1], list(Bet.get_by_bettable_and_has_result_and_bettable_has_result(g1.pk)))
        self.assertItemsEqual([], list(Bet.get_by_bettable_and_has_result_and_bettable_has_result(g2.pk)))
        self.assertItemsEqual([bet6], list(Bet.get_by_bettable_and_has_result_and_bettable_has_result(g3.pk)))

    def test_get_user_bettable_bet(self):
        u1, u2 = utils.create_user(), utils.create_user()
        g1, g2 = utils.create_game(), utils.create_game()

        bet1 = utils.create_bet(u1, g1)
        bet2 = utils.create_bet(u1, g2)
        bet3 = utils.create_bet(u2, g1)

        self.assertEqual(bet1, Bet.get_user_bettable_bet(u1.pk, g1.pk))
        self.assertEqual(bet2, Bet.get_user_bettable_bet(u1.pk, g2.pk))
        self.assertEqual(bet3, Bet.get_user_bettable_bet(u2.pk, g1.pk))
        self.assertIsNone(Bet.get_user_bettable_bet(u2.pk, g2.pk))

    def test_compute_points_of_game_bettable_none(self):
        u, g, g_r = utils.create_user(), utils.create_game(), utils.create_game(homegoals=3, awaygoals=1)

        # game has no result
        bet1 = utils.create_bet(u, g, result_bet="3:1")
        bet1.compute_points_of_game_bettable()
        self.assertIsNone(bet1.result_bet_type)

        # no bet was set
        bet2 = utils.create_bet(u, g_r)
        bet2.compute_points_of_game_bettable()
        self.assertIsNone(bet2.result_bet_type)

    def test_compute_points_of_game_bettable_volltreffer(self):
        u, g, g_r = utils.create_user(), utils.create_game(homegoals=3, awaygoals=1), \
                    utils.create_game(homegoals=1, awaygoals=1)

        gb = utils.create_bet(u, g, result_bet="3:1")
        gb.compute_points_of_game_bettable()
        self.assertEqual('volltreffer', gb.result_bet_type)

        gb = utils.create_bet(u, g_r, result_bet="1:1")
        gb.compute_points_of_game_bettable()
        self.assertEqual('volltreffer', gb.result_bet_type)

    def test_compute_points_of_game_bettable_differenz(self):
        u, g = utils.create_user(), utils.create_game(homegoals=4, awaygoals=0)

        gb = utils.create_bet(u, g, result_bet="6:2")
        gb.compute_points_of_game_bettable()
        self.assertEqual('differenz', gb.result_bet_type)

    def test_compute_points_of_game_bettable_remis_tendenz(self):
        u, g = utils.create_user(), utils.create_game(homegoals=1, awaygoals=1)

        gb = utils.create_bet(u, g, result_bet="3:3")
        gb.compute_points_of_game_bettable()
        self.assertEqual('remis_tendenz', gb.result_bet_type)

    def test_compute_points_of_game_bettable_tendenz(self):
        u, g = utils.create_user(), utils.create_game(homegoals=2, awaygoals=0)

        gb = utils.create_bet(u, g, result_bet="3:0")
        gb.compute_points_of_game_bettable()
        self.assertEqual('tendenz', gb.result_bet_type)

        Bet.objects.all().delete()

        gb = utils.create_bet(u, g, result_bet="3:2")
        gb.compute_points_of_game_bettable()
        self.assertEqual('tendenz', gb.result_bet_type)

    def test_compute_points_of_game_bettable_niete(self):
        u, g, g_r = utils.create_user(), utils.create_game(homegoals=2, awaygoals=1), \
                    utils.create_game(homegoals=0, awaygoals=0)

        gb = utils.create_bet(u, g, result_bet="0:1")
        gb.compute_points_of_game_bettable()
        self.assertEqual('niete', gb.result_bet_type)

        gb = utils.create_bet(u, g_r, result_bet="1:2")
        gb.compute_points_of_game_bettable()
        self.assertEqual('niete', gb.result_bet_type)

    def assertItemsEqual(self, list1, list2):
        self.assertEqual(len(list1), len(list2))
        for list1_item in list1:
            self.assertTrue(list1_item in list2)