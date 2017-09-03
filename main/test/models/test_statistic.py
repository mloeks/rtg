# -*- coding: utf-8 -*-
import time
from random import randrange

from django.contrib.auth.models import User
from django.test import TestCase

from main.models import Statistic
from main.test.utils import TestModelUtils as utils


class StatisticTests(TestCase):

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

    def test_recalculate(self):
        utils.create_gamebet_result_types()
        u1, u2 = utils.create_user('Queen'), utils.create_user('King')

        g1 = utils.create_game(homegoals=3, awaygoals=1)
        g2 = utils.create_game(homegoals=0, awaygoals=0)
        g3 = utils.create_game(homegoals=2, awaygoals=1)
        g4 = utils.create_game(homegoals=2, awaygoals=4)
        g5 = utils.create_game()

        e1 = utils.create_extra(points=7, result='Schweiz')
        utils.create_extrachoice(name='Deutschland', extra=e1)
        utils.create_extrachoice(name='Schweiz', extra=e1)

        gb1 = utils.create_gamebet(u1, g1, 3, 1)
        gb2 = utils.create_gamebet(u1, g2, 1, 1)
        gb3 = utils.create_gamebet(u1, g3, 3, 0)
        gb4 = utils.create_gamebet(u1, g4, 2, 2)
        gb5 = utils.create_gamebet(u1, g5, 0, 2)
        eb1 = utils.create_extrabet('Deutschland', e1, u1)

        gb6 = utils.create_gamebet(u2, g1, 4, 2)
        eb2 = utils.create_extrabet('Schweiz', e1, u2)

        # statistics should be recalculated when games or extras are saved
        [g.save() for g in [g1, g2, g3, g4, g5]]
        e1.save()

        u1_stats = Statistic.objects.get(user=u1)
        u2_stats = Statistic.objects.get(user=u2)

        self.assertEqual(6, u1_stats.no_bets)
        self.assertEqual(1, u1_stats.no_volltreffer)
        self.assertEqual(8, u1_stats.points)

        self.assertEqual(2, u2_stats.no_bets)
        self.assertEqual(1, u2_stats.no_volltreffer)
        self.assertEqual(10, u2_stats.points)

    def test_many_users(self):
        utils.create_gamebet_result_types()

        USERS=20
        GAMES=10
        BET_AMOUNT=0.6

        start_time = time.clock()
        print("~"*50)
        print("SCALING test START = %s" % start_time)

        # create many users
        users = []
        for i in range(0, USERS):
            users.append(utils.create_user())

        # create many games
        games = []
        for i in range(0, GAMES):
            g, r = utils.create_group(), utils.create_round()
            games.append(utils.create_game(hometeam=utils.create_team(name='H%i' % i, group=g),
                                           awayteam=utils.create_team(name='A%i' % i, group=g),
                                           round=r))

        # create gamebets for the given amount of the games for all users and save them
        bets = []
        for u in users:
            for g in games[0:int(BET_AMOUNT*len(games))]:
                bet = utils.create_gamebet(u, g, randrange(6), randrange(6))
                bet.save()
                bets.append(bet)

        # create results for all games and save them
        game_save_times = []
        for g in games:
            g.homegoals, g.awaygoals = randrange(6), randrange(6)
            game_save_start = time.clock()
            g.save()
            game_save_end = time.clock()
            game_save_times.append(game_save_end - game_save_start)

        avg_game_save = sum(game_save_times) / len(game_save_times)

        end_time = time.clock()
        duration = (end_time - start_time)
        print("SCALING test FINISHED = %s" % end_time)
        print("TOOK %f s altogether" % duration)
        print("TOOK %f s on average per game save" % avg_game_save)
        print("~"*50)
        print("~"*50)

        print("USER STATISTICS:")
        ranked_users = sorted(list(User.objects.all().order_by('username')),
                              key=lambda it: (it.statistic.points, it.statistic.no_volltreffer, it.statistic.no_bets),
                              reverse=True)
        for u in ranked_users:
            print(u.statistic.pretty_print())

        self.assertEqual(int(BET_AMOUNT*len(games)), users[0].statistic.no_bets)
        # TODO what else could be asserted?