# -*- coding: utf-8 -*-
import time
from datetime import datetime
from random import randrange

from django.contrib.auth.models import User
from django.test import TestCase

from main.models import Statistic, ResultBetType, timedelta
from main.test.utils import TestModelUtils as utils


class StatisticTests(TestCase):
    """
        These tests should test the methods in Statistic model class only.
        Required testing states should be set up in the tests.
        No post_save hooks are tested here.
    """

    def tearDown(self):
        User.objects.all().delete()
        Statistic.objects.all().delete()

    def test_create_statistic_after_user(self):
        u1 = utils.create_user('Queen')
        self.assertIsNotNone(u1.statistic)

        s = Statistic.objects.get(user=u1)
        self.assertIsNotNone(s)
        self.assertEqual("Queen's statistics", str(s))
        self.assertEqual(0, s.no_volltreffer)
        self.assertEqual(0, s.no_bets)
        self.assertEqual(0, s.points)

    def test_simple_recalculate(self):
        # GIVEN: some user
        u1 = utils.create_user('Queen')

        # AND: any two games
        g1 = utils.create_game(homegoals=3, awaygoals=1)
        g2 = utils.create_game()

        # AND: some bets for these games with result type and points
        utils.create_bet(u1, g1, "4:2", ResultBetType.differenz.name, 3)
        utils.create_bet(u1, g2, "3:0")  # no result since game has no result yet

        # WHEN stats are updated
        u1_stats = Statistic.objects.get(user=u1)
        u1_stats.update()

        # THEN: the stats are as expected
        self.assertEqual(2, u1_stats.no_bets)
        self.assertEqual(0, u1_stats.no_volltreffer)
        self.assertEqual(1, u1_stats.no_differenz)
        self.assertEqual(0, u1_stats.no_tendenz)
        self.assertEqual(0, u1_stats.no_remis_tendenz)
        self.assertEqual(0, u1_stats.no_niete)
        self.assertEqual(3, u1_stats.points)

    def test_no_calc_before_tournament(self):
        # GIVEN: some user
        u1 = utils.create_user('Queen')

        # AND: some game in the future
        g1 = utils.create_game(homegoals=2, awaygoals=4, kickoff=datetime.now() + timedelta(days=5))

        # AND: some bet for this game with result type and points
        utils.create_bet(u1, g1, "2:3", ResultBetType.tendenz.name, 1)

        # WHEN: stats are updated
        u1_stats = Statistic.objects.get(user=u1)
        u1_stats.update()

        # THEN: the stats should be all-0, because the tournament has not yet started
        self.assertEqual(0, u1_stats.no_bets)
        self.assertEqual(0, u1_stats.no_volltreffer)
        self.assertEqual(0, u1_stats.no_differenz)
        self.assertEqual(0, u1_stats.no_tendenz)
        self.assertEqual(0, u1_stats.no_remis_tendenz)
        self.assertEqual(0, u1_stats.no_niete)
        self.assertEqual(0, u1_stats.points)

    def test_recalculate(self):
        # GIVEN: some users
        u1, u2 = utils.create_user('Queen'), utils.create_user('King')

        # AND: some games
        g1 = utils.create_game(homegoals=3, awaygoals=1)
        g2 = utils.create_game(homegoals=0, awaygoals=0)
        g3 = utils.create_game(homegoals=2, awaygoals=1)
        g4 = utils.create_game(homegoals=2, awaygoals=4)
        g5 = utils.create_game()

        # AND: some extras
        e1 = utils.create_extra(points=7, result='Schweiz')
        utils.create_extrachoice(name='Deutschland', extra=e1)
        utils.create_extrachoice(name='Schweiz', extra=e1)

        # AND: some bets, with points - if bettable is finished
        utils.create_bet(u1, g1, "3:1", ResultBetType.volltreffer.name, 5)
        utils.create_bet(u1, g2, "1:1", ResultBetType.remis_tendenz.name, 2)
        utils.create_bet(u1, g3, "3:0", ResultBetType.tendenz.name, 1)
        utils.create_bet(u1, g4, "2:2", ResultBetType.niete.name, 0)
        utils.create_bet(u1, g5, "0:2")
        utils.create_bet(u1, e1, 'Deutschland', ResultBetType.niete.name, 0)

        utils.create_bet(u2, g1, "4:2", ResultBetType.differenz.name, 3)
        utils.create_bet(u2, e1, 'Schweiz', ResultBetType.volltreffer.name, 10)

        # WHEN: stats are updated
        u1_stats = Statistic.objects.get(user=u1)
        u1_stats.update()

        u2_stats = Statistic.objects.get(user=u2)
        u2_stats.update()

        # THEN: the stats of user 1 should be as expected
        self.assertEqual(6, u1_stats.no_bets)
        self.assertEqual(8, u1_stats.points)
        self.assertEqual(1, u1_stats.no_volltreffer)
        self.assertEqual(0, u1_stats.no_differenz)
        self.assertEqual(1, u1_stats.no_remis_tendenz)
        self.assertEqual(1, u1_stats.no_tendenz)
        self.assertEqual(2, u1_stats.no_niete)

        # AND: the stats of user 2 should be as expected
        self.assertEqual(2, u2_stats.no_bets)
        self.assertEqual(13, u2_stats.points)
        self.assertEqual(1, u2_stats.no_volltreffer)
        self.assertEqual(1, u2_stats.no_differenz)
        self.assertEqual(0, u2_stats.no_remis_tendenz)
        self.assertEqual(0, u2_stats.no_tendenz)
        self.assertEqual(0, u2_stats.no_niete)
