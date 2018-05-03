# -*- coding: utf-8 -*-
import time
from random import randrange

from django.contrib.auth.models import User
from django.test import TestCase

from main.models import Statistic, ResultBetType
from main.test.utils import TestModelUtils as utils


class BetResultUpdateTests(TestCase):
    """
        These tests should test the correct update of all bet's points withi the post_save hooks in the models.py
        They actually have the character of an integration test, because they test working functionality
        across multiple models.
    """

    def tearDown(self):
        User.objects.all().delete()
        Statistic.objects.all().delete()

    def test_simple_update(self):
        # GIVEN: some user
        some_user = utils.create_user('Queen')

        # AND: any two games
        g1, g2 = utils.create_game(), utils.create_game()

        # AND: some bets for these games
        b1 = utils.create_bet(some_user, g1, "4:2")
        b2 = utils.create_bet(some_user, g2, "3:0")

        # WHEN games get a result and are saved
        g1.homegoals = 3
        g1.awaygoals = 1
        g1.save()
        g2.homegoals = 1
        g2.awaygoals = 1
        g2.save()

        # THEN: the user stats are as expected
        user_stats = Statistic.objects.get(user=some_user)
        self.assertEqual(2, user_stats.no_bets)
        self.assertEqual(0, user_stats.no_volltreffer)
        self.assertEqual(1, user_stats.no_differenz)
        self.assertEqual(0, user_stats.no_tendenz)
        self.assertEqual(0, user_stats.no_remis_tendenz)
        self.assertEqual(1, user_stats.no_niete)
        self.assertEqual(3, user_stats.points)

    def test_more_complex_update(self):
        # GIVEN: two users
        u1, u2 = utils.create_user('Queen'), utils.create_user('King')

        # AND: some games
        g1, g3, g4, g5 = utils.create_game(), utils.create_game(), utils.create_game(), utils.create_game()
        g2 = utils.create_game(homegoals=0, awaygoals=0)

        # AND: some extras
        e1 = utils.create_extra(points=7, result='Schweiz')
        e2 = utils.create_extra(points=7)
        utils.create_extrachoice(name='Deutschland', extra=e1)
        utils.create_extrachoice(name='Schweiz', extra=e1)
        utils.create_extrachoice(name='Niederlande', extra=e2)
        utils.create_extrachoice(name='Belgien', extra=e2)

        # AND: some bets
        utils.create_bet(u1, g1, "3:1")
        utils.create_bet(u1, g2, "1:1")
        utils.create_bet(u1, g3, "3:0")
        utils.create_bet(u1, g4, "2:2")
        utils.create_bet(u1, g5, "0:2")
        utils.create_bet(u1, e1, 'Deutschland')
        utils.create_bet(u1, e2, 'Niederlande')

        utils.create_bet(u2, g1, "4:2")
        utils.create_bet(u2, g4, "2:1")
        utils.create_bet(u2, g5, "0:0")
        utils.create_bet(u2, e1, 'Schweiz')
        utils.create_bet(u2, e2, 'Belgien')

        # WHEN: bettable result's are updated
        g1.set_result_goals(3, 1)
        g2.remove_result()
        g3.set_result_goals(2, 1)
        g4.set_result_goals(2, 4)
        g5.set_result_goals(1, 1)

        e1.remove_result()
        e2.set_result('Niederlande')

        # THEN: the stats of user 1 should be as expected
        u1_stats = Statistic.objects.get(user=u1)
        self.assertEqual(7, u1_stats.no_bets)
        self.assertEqual(13, u1_stats.points)
        self.assertEqual(2, u1_stats.no_volltreffer)
        self.assertEqual(0, u1_stats.no_differenz)
        self.assertEqual(0, u1_stats.no_remis_tendenz)
        self.assertEqual(1, u1_stats.no_tendenz)
        self.assertEqual(2, u1_stats.no_niete)

        # AND: the stats of user 2 should be as expected
        u2_stats = Statistic.objects.get(user=u2)
        self.assertEqual(5, u2_stats.no_bets)
        self.assertEqual(5, u2_stats.points)
        self.assertEqual(0, u2_stats.no_volltreffer)
        self.assertEqual(1, u2_stats.no_differenz)
        self.assertEqual(1, u2_stats.no_remis_tendenz)
        self.assertEqual(0, u2_stats.no_tendenz)
        self.assertEqual(2, u2_stats.no_niete)

    def test_many_users(self):
        """
            "performance test" which should give an indication about how fast the recalculation of bet points
            is with many users
        """
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

        # create bets for the given amount of the games for all users and save them
        bets = []
        for u in users:
            for g in games[0:int(BET_AMOUNT*len(games))]:
                bet = utils.create_bet(u, g, "%s:%s" % (randrange(6), randrange(6)))
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
        # TODO P3 what else could be asserted?
