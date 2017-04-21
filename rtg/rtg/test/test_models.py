# -*- coding: utf-8 -*-
import time
from datetime import timedelta
from random import randrange

from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.db import transaction, IntegrityError, DataError
from django.test import TestCase
from django.utils import timezone

from rtg.models import Profile, TournamentGroup, TournamentRound, Game, Venue, Team, GameBet, GameBetResult, Extra, \
    ExtraChoice, ExtraBet, Post, Statistic
from rtg.test.utils import TestModelUtils as utils


class TournamentGroupTests(TestCase):

    def tearDown(self):
        utils.cleanup()

    def test_to_string(self):
        TournamentGroup.objects.create(name="Testgruppe", abbreviation="TGR")

        group = TournamentGroup.objects.get(name='Testgruppe')
        self.assertIsNotNone(group)
        self.assertEqual('Testgruppe', group.name)
        self.assertEqual('TGR', group.abbreviation)
        self.assertEqual('Testgruppe', str(group))

    def test_ordering(self):
        TournamentGroup.objects.create(name="Gruppe C", abbreviation="C")
        TournamentGroup.objects.create(name="Gruppe A", abbreviation="A")
        TournamentGroup.objects.create(name="Gruppe B", abbreviation="B")

        groups = list(TournamentGroup.objects.all())
        self.assertListEqual(['A', 'B', 'C'], [gr.abbreviation for gr in groups])

    def test_invalid_missing_fields(self):
        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                TournamentGroup.objects.create(name=None, abbreviation="ABB")

        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                TournamentGroup.objects.create(name="Gruppe", abbreviation=None)

    def test_invalid_field_restrictions(self):
        with self.assertRaises(DataError):
            with transaction.atomic():
                TournamentGroup.objects.create(name=u"Dieser Gruppenname ist länger als erlaubt!", abbreviation="ABC")
        with self.assertRaises(DataError):
            with transaction.atomic():
                TournamentGroup.objects.create(name="Gruppe", abbreviation="LANG")

    def test_invalid_duplicates(self):
        TournamentGroup.objects.create(name="Gruppe C", abbreviation="C")
        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                TournamentGroup.objects.create(name="Gruppe C", abbreviation="A")

        TournamentGroup.objects.create(name="Gruppe D", abbreviation="D")
        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                TournamentGroup.objects.create(name="Gruppe A", abbreviation="D")


class TournamentRoundTests(TestCase):

    def tearDown(self):
        utils.cleanup()

    def test_to_string(self):
        TournamentRound.objects.create(name="Testrunde", display_order=1)

        round = TournamentRound.objects.get(name='Testrunde')
        self.assertIsNotNone(round)
        self.assertEqual('Testrunde', round.name)
        self.assertEqual('Testrunde', str(round))

    def test_ordering(self):
        TournamentRound.objects.create(name="Vorrunde", display_order=1, abbreviation="VOR")
        TournamentRound.objects.create(name="Halbfinale", display_order=3, abbreviation="HF")
        TournamentRound.objects.create(name="Achtelfinale", display_order=2, abbreviation="AF")

        rounds = list(TournamentRound.objects.all())
        self.assertListEqual(['VOR', 'AF', 'HF'], [r.abbreviation for r in rounds])

    def test_invalid_missing_fields(self):
        # is_knock_out and abbreviation are optional
        TournamentRound.objects.create(name='Testrunde', display_order=123)

        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                TournamentRound.objects.create(name=None, display_order=123)
        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                TournamentRound.objects.create(name='Testrunde')

    def test_invalid_field_restrictions(self):
        with self.assertRaises(DataError):
            with transaction.atomic():
                TournamentRound.objects.create(name=51*'z', display_order=123)

    def test_invalid_duplicates(self):
        TournamentRound.objects.create(name="Runde A", display_order=1)
        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                TournamentRound.objects.create(name="Runde A", display_order=2)

    def test_get_all_games(self):
        r1 = utils.create_round()
        r2 = utils.create_round()

        g1 = utils.create_game(round=r1)
        g2 = utils.create_game(round=r2)
        g3 = utils.create_game(round=r1)
        g4 = utils.create_game(round=r2)
        g5 = utils.create_game(round=r2)

        self.assertListEqual([g1, g3], list(r1.get_all_games()))
        self.assertListEqual([g2, g4, g5], list(r2.get_all_games()))


class TeamTests(TestCase):

    def setUp(self):
        self.g1, self.g2 = utils.create_group(), utils.create_group()

    def tearDown(self):
        utils.cleanup()

    def test_to_string(self):
        Team.objects.create(name="A-Team", abbreviation="AT", group=self.g1)

        team = Team.objects.get(name='A-Team')
        self.assertIsNotNone(team)
        self.assertEqual('A-Team', team.name)
        self.assertEqual('AT', team.abbreviation)
        self.assertEqual('A-Team', str(team))

    def test_ordering(self):
        Team.objects.create(name="Borussia Dortmund", abbreviation="DOR", group=self.g1)
        Team.objects.create(name=u"1860 München", abbreviation="MUN", group=self.g2)
        Team.objects.create(name="TSG 1899 Hoffenheim", abbreviation="HOF", group=self.g1)

        teams = list(Team.objects.all())
        self.assertListEqual(['MUN', 'DOR', 'HOF'], [t.abbreviation for t in teams])

    def test_invalid_missing_fields(self):
        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                Team.objects.create(name=None, abbreviation="BVB", group=self.g1)
        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                Team.objects.create(name="Borussia Dortmund", abbreviation=None, group=self.g1)
        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                Team.objects.create(name=u"1. FC Köln", abbreviation='FC')

    def test_invalid_field_restrictions(self):
        with self.assertRaises(DataError):
            with transaction.atomic():
                Team.objects.create(name=51*'z', abbreviation="ABC", group=self.g1)
        with self.assertRaises(DataError):
            with transaction.atomic():
                Team.objects.create(name="Team", abbreviation="LANG", group=self.g2)

    def test_invalid_duplicates(self):
        Team.objects.create(name="A-Team", abbreviation="AT", group=self.g1)
        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                Team.objects.create(name="A-Team", abbreviation="AAA", group=self.g2)
        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                Team.objects.create(name="B-Team", abbreviation="AT", group=self.g1)


class VenueTests(TestCase):

    def tearDown(self):
        utils.cleanup()

    def test_to_string(self):
        Venue.objects.create(name="Citi Field", city="New York City", capacity=40000)

        venue = Venue.objects.get(name='Citi Field')
        self.assertIsNotNone(venue)
        self.assertEqual('Citi Field', venue.name)
        self.assertEqual('New York City', venue.city)
        self.assertEqual(40000, venue.capacity)
        self.assertEqual('Citi Field (New York City)', str(venue))

    def test_ordering(self):
        Venue.objects.create(name='Glitzerfeld', city='Glamour City')
        Venue.objects.create(name='Rosenhof', city='Glamour City')
        Venue.objects.create(name='1st Main Plaza Field', city='Glamour City')

        venues = list(Venue.objects.all())
        self.assertListEqual(['1st Main Plaza Field', 'Glitzerfeld', 'Rosenhof'], [v.name for v in venues])

    def test_invalid_missing_fields(self):
        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                Venue.objects.create(name=None, city=u"Köln", capacity=123)
        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                Venue.objects.create(name=u'Südstadion', city=None, capacity=456)
        # capacity is optional
        Venue.objects.create(name=u"1. FC Köln", city=u'Köln')

    def test_invalid_field_restrictions(self):
        with self.assertRaises(DataError):
            with transaction.atomic():
                Venue.objects.create(name=51*'z', city="Nordhorn", capacity=123)
        with self.assertRaises(DataError):
            with transaction.atomic():
                Venue.objects.create(name='Stadion', city=51*'z', capacity=456)
        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                Venue.objects.create(name='Stadion', city='Stadt', capacity=-1)

    def test_invalid_duplicates(self):
        Venue.objects.create(name="Signal Iduna Park", city="Dortmund", capacity=81000)
        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                Venue.objects.create(name="Signal Iduna Park", city="DO", capacity=82000)
        # city must not be unique
        Venue.objects.create(name="Rote Erde", city="Dortmund", capacity=25000)


class GameTests(TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        Game.objects.all().delete()
        Team.objects.all().delete()
        utils.cleanup()

    def test_to_string(self):
        t1, t2 = utils.create_team(), utils.create_team()
        g1 = utils.create_game(hometeam=t1, awayteam=t2)
        self.assertEqual('%s - %s' % (t1.name, t2.name), str(g1))

    def test_ordering(self):
        g1 = utils.create_game(kickoff=utils.create_datetime_from_now())
        g2 = utils.create_game(kickoff=utils.create_datetime_from_now(timedelta(hours=-3)))
        g3 = utils.create_game(kickoff=utils.create_datetime_from_now(timedelta(days=2)))
        g4 = utils.create_game(kickoff=utils.create_datetime_from_now(timedelta(hours=2)))

        self.assertListEqual([g2, g1, g4, g3], list(Game.objects.all()))

    def test_invalid_missing_fields(self):
        # test that optional fields work
        t1, t2 = utils.create_team(), utils.create_team()
        v1, r1 = utils.create_venue(), utils.create_round()
        Game.objects.create(kickoff=timezone.now(), deadline=timezone.now(),
                            hometeam=t1, awayteam=t2, venue=v1, round=r1)

        # test that missing required fields raise an error
        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                Game.objects.create(kickoff=timezone.now(), hometeam=t1, awayteam=t2, venue=v1, round=r1)
        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                Game.objects.create(deadline=timezone.now(), hometeam=t1, awayteam=t2, venue=v1, round=r1)
        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                Game.objects.create(kickoff=timezone.now(), deadline=timezone.now(), awayteam=t2, venue=v1, round=r1)
        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                Game.objects.create(kickoff=timezone.now(), deadline=timezone.now(), hometeam=t1, venue=v1, round=r1)
        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                Game.objects.create(kickoff=timezone.now(), deadline=timezone.now(),
                                    hometeam=t1, awayteam=t2, round=r1)
        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                Game.objects.create(kickoff=timezone.now(), deadline=timezone.now(),
                                    hometeam=t1, awayteam=t2, venue=v1)

    def test_invalid_field_deadline(self):
        t1, t2 = utils.create_team(), utils.create_team()
        v1, r1 = utils.create_venue(), utils.create_round()
        now = timezone.now()

        # deadline must not be later than kickoff
        g3 = Game.objects.create(kickoff=now, deadline=now + timedelta(hours=2),
                                 hometeam=t1, awayteam=t2, venue=v1, round=r1)
        self.assertRaises(ValidationError, g3.clean)

    def test_invalid_field_teams(self):
        t1, t2 = utils.create_team(), utils.create_team()
        v1, r1 = utils.create_venue(), utils.create_round()
        now = timezone.now()

        # teams cannot be equal
        g1 = Game.objects.create(kickoff=now, deadline=now, hometeam=t1, awayteam=t1, venue=v1, round=r1)
        self.assertRaises(ValidationError, g1.clean)

    def test_invalid_field_teams_rounds(self):
        r1, r2 = utils.create_round(), utils.create_round(is_knock_out=True)
        gr1, gr2 = utils.create_group(), utils.create_group()
        t1, t2, t3 = utils.create_team(group=gr1), utils.create_team(group=gr2), utils.create_team(group=gr1)
        v1 = utils.create_venue()
        now = timezone.now()

        # these should be OK
        Game.objects.create(kickoff=now, deadline=now, hometeam=t1, awayteam=t3, venue=v1, round=r1).clean()
        Game.objects.create(kickoff=now, deadline=now, hometeam=t1, awayteam=t2, venue=v1, round=r2).clean()

        # this game is not possible
        g1 = Game.objects.create(kickoff=now, deadline=now, hometeam=t1, awayteam=t2, venue=v1, round=r1)
        self.assertRaises(ValidationError, g1.clean)

    def test_result_str(self):
        g1_result = utils.create_game(homegoals=4, awaygoals=2)
        g2_noresult = utils.create_game(homegoals=-1, awaygoals=-1)

        self.assertEqual('4:2', g1_result.result_str())
        self.assertEqual('-:-', g2_noresult.result_str())

    def test_has_started(self):
        now = utils.create_datetime_from_now()
        g1 = utils.create_game(kickoff=now)
        g2 = utils.create_game(kickoff=now + timedelta(seconds=-1))
        g3 = utils.create_game(kickoff=now + timedelta(seconds=1))
        g4 = utils.create_game(kickoff=now + timedelta(hours=2))

        self.assertTrue(g1.has_started())
        self.assertTrue(g2.has_started())
        self.assertFalse(g3.has_started())
        self.assertFalse(g4.has_started())

    def test_is_over(self):
        now = utils.create_datetime_from_now()
        g1 = utils.create_game(kickoff=now)
        g2 = utils.create_game(kickoff=now + timedelta(hours=-1, minutes=-46))
        g3 = utils.create_game(kickoff=now + timedelta(days=-1))
        g4 = utils.create_game(kickoff=now + timedelta(hours=2))

        self.assertFalse(g1.is_over())
        self.assertTrue(g2.is_over())
        self.assertTrue(g3.is_over())
        self.assertFalse(g4.is_over())

    def test_has_result(self):
        self.assertFalse(utils.create_game().has_result())
        self.assertFalse(utils.create_game(homegoals=3).has_result())
        self.assertFalse(utils.create_game(awaygoals=0).has_result())
        self.assertTrue(utils.create_game(homegoals=4, awaygoals=1).has_result())

    def test_get_finished_games(self):
        g1 = utils.create_game()
        g2 = utils.create_game(homegoals=3, awaygoals=0)
        g3 = utils.create_game(homegoals=2)

        self.assertListEqual([g2], list(Game.get_finished_games()))

    def test_get_games_deadline_passed(self):
        now = utils.create_datetime_from_now()
        g1 = utils.create_game(kickoff=now)
        g2 = utils.create_game(kickoff=now + timedelta(seconds=-1))
        g3 = utils.create_game(kickoff=now + timedelta(seconds=1))
        g4 = utils.create_game(kickoff=now + timedelta(hours=2))

        self.assertListEqual([g2, g1], list(Game.get_games_deadline_passed()))

    def test_get_latest_finished_game(self):
        now = utils.create_datetime_from_now()
        g1 = utils.create_game(kickoff=now + timedelta(days=-3), homegoals=3, awaygoals=1)
        g2 = utils.create_game(kickoff=now + timedelta(days=-2), homegoals=4, awaygoals=0)
        g3 = utils.create_game(kickoff=now + timedelta(days=-1))
        g4 = utils.create_game(kickoff=now)
        g5 = utils.create_game(kickoff=now + timedelta(days=3))

        self.assertEqual(g2, Game.get_latest_finished_game())

    def test_get_first_game(self):
        now = utils.create_datetime_from_now()
        g1 = utils.create_game(kickoff=now)
        g2 = utils.create_game(kickoff=now + timedelta(seconds=-1))
        g3 = utils.create_game(kickoff=now + timedelta(seconds=1))
        g4 = utils.create_game(kickoff=now + timedelta(hours=2))

        self.assertEqual(g2, Game.get_first_game())


class GameBetResultTests(TestCase):

    def tearDown(self):
        utils.cleanup()

    def test_to_string(self):
        GameBetResult.objects.create(type="Volltreffer", points=111, sort_id='abc')

        gamebetresult = GameBetResult.objects.get(type='Volltreffer')
        self.assertIsNotNone(gamebetresult)
        self.assertEqual('Volltreffer', gamebetresult.type)
        self.assertEqual(111, gamebetresult.points)
        self.assertEqual('abc', gamebetresult.sort_id)
        self.assertEqual('Volltreffer', str(gamebetresult))

    def test_ordering(self):
        GameBetResult.objects.create(type='Volltreffer', points=10, sort_id='abc')
        GameBetResult.objects.create(type='00 Niete', points=1, sort_id='bb')
        GameBetResult.objects.create(type='tendenz', points=3, sort_id='123')

        gamebetresults = list(GameBetResult.objects.all())
        self.assertListEqual(['tendenz', 'Volltreffer', '00 Niete'], [gbr.type for gbr in gamebetresults])

    def test_invalid_missing_fields(self):
        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                GameBetResult.objects.create(type=None, points=111, sort_id='123')
        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                GameBetResult.objects.create(type='Volltreffer', sort_id='123')
        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                GameBetResult.objects.create(type='Volltreffer', points=111, sort_id=None)

    def test_invalid_field_restrictions(self):
        with self.assertRaises(DataError):
            with transaction.atomic():
                GameBetResult.objects.create(type=51*'z', points=111, sort_id='123')
        with self.assertRaises(DataError):
            with transaction.atomic():
                GameBetResult.objects.create(type='Volltreffer', points=111, sort_id='too long')

    def test_invalid_duplicates(self):
        GameBetResult.objects.create(type="Differenz", points=123, sort_id='abc')
        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                GameBetResult.objects.create(type="Differenz", points=5, sort_id='yyy')
        # sort_id must not be unique
        GameBetResult.objects.create(type="Tendenz", points=222, sort_id='abc')


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
        with self.assertRaises(ValueError):
            with transaction.atomic():
                GameBet.objects.create(game=g, user=None)
        with self.assertRaises(ValueError):
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
        g1, g2, g3 = utils.create_game(homegoals=3, awaygoals=2),\
                     utils.create_game(),\
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


class ExtraTests(TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        Extra.objects.all().delete()
        utils.cleanup()

    def test_to_string(self):
        e = Extra.objects.create(name='RTG-Meister', deadline=timezone.now())
        self.assertEqual('RTG-Meister', str(e))

    def test_invalid_missing_fields(self):
        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                Extra.objects.create(name=None, points=123, deadline=timezone.now(), result='Die Königin')
        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                Extra.objects.create(name='RTG-Meister', points=123, deadline=None, result='Die Königin')

        # result may be blank but not null
        Extra.objects.create(name='RTG-Meister', deadline=timezone.now(), result='')
        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                Extra.objects.create(name='RTG-Zweiter', deadline=timezone.now(), result=None)

    def test_invalid_fields(self):
        with self.assertRaises(DataError):
            with transaction.atomic():
                Extra.objects.create(name=51*'z', deadline=timezone.now())
        with self.assertRaises(DataError):
            with transaction.atomic():
                Extra.objects.create(name='RTG-Meister', deadline=timezone.now(), result=51*'y')

        # name must be unique
        Extra.objects.create(name='RTG-Meister', deadline=timezone.now())
        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                Extra.objects.create(name='RTG-Meister', deadline=timezone.now())

    def test_has_result(self):
        e1, e2 = utils.create_extra(), utils.create_extra(result='Die Königin!')

        self.assertFalse(e1.has_result())
        self.assertTrue(e2.has_result())

    def test_deadline_passed(self):
        now = utils.create_datetime_from_now()
        self.assertTrue(utils.create_extra().deadline_passed())
        self.assertTrue(utils.create_extra(deadline=now + timedelta(hours=-2)).deadline_passed())
        self.assertFalse(utils.create_extra(deadline=now + timedelta(hours=2)).deadline_passed())

    def test_get_finished_extras(self):
        e1, e2, e3 = utils.create_extra(result='Die Königin!'), utils.create_extra(), \
                     utils.create_extra(result='Der Prinzgemahl!')

        self.assertListEqual([e1, e3], list(Extra.get_finished_extras()))


class ExtraChoiceTests(TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        ExtraChoice.objects.all().delete()
        utils.cleanup()

    def test_to_string(self):
        e = utils.create_extra()
        ec = ExtraChoice.objects.create(name='Schweden', extra=e)
        self.assertEqual('Schweden', str(ec))

    def test_ordering(self):
        e1 = utils.create_extrachoice(sort_index='Test')
        e2 = utils.create_extrachoice(sort_index='123abc')
        e3 = utils.create_extrachoice(sort_index='schweden')

        self.assertListEqual([e2, e3, e1], list(ExtraChoice.objects.all()))

    def test_invalid_missing_fields(self):
        e = utils.create_extra()
        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                ExtraChoice.objects.create(name=None, extra=e, sort_index='abc')
        with self.assertRaises(ValueError):
            with transaction.atomic():
                ExtraChoice.objects.create(name='Schweden', extra=None, sort_index='def')

        # sort_index may be blank but not None
        ExtraChoice.objects.create(name='Nederland', extra=e, sort_index='abc')
        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                ExtraChoice.objects.create(name='France', extra=e, sort_index=None)

    def test_invalid_fields(self):
        e1, e2 = utils.create_extra(), utils.create_extra()

        with self.assertRaises(DataError):
            with transaction.atomic():
                ExtraChoice.objects.create(name=51*'z', extra=e1, sort_index='abc')
        with self.assertRaises(DataError):
            with transaction.atomic():
                ExtraChoice.objects.create(name='Sverige', extra=e2, sort_index=11*'y')

        # there may exist name duplicates, but not within the same Extra
        ExtraChoice.objects.create(name='Italia', extra=e1)
        with transaction.atomic():
            ExtraChoice.objects.create(name='Italia', extra=e2)
        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                ExtraChoice.objects.create(name='Italia', extra=e1)

    def test_has_result(self):
        e1, e2 = utils.create_extra(), utils.create_extra(result='Die Königin!')

        self.assertFalse(e1.has_result())
        self.assertTrue(e2.has_result())


class ExtraBetTests(TestCase):

    def tearDown(self):
        utils.cleanup()

    def test_to_string(self):
        e, u = utils.create_extra(), utils.create_user()
        eb = ExtraBet.objects.create(result_bet='Deutschland', extra=e, user=u)
        self.assertEqual('Deutschland', str(eb))

    def test_invalid_missing_fields(self):
        e1, e2, u = utils.create_extra(), utils.create_extra(), utils.create_user()
        ExtraBet.objects.create(result_bet='', extra=e1, user=u)
        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                ExtraBet.objects.create(result_bet=None, extra=e2, user=u)
        with self.assertRaises(ValueError):
            with transaction.atomic():
                ExtraBet.objects.create(result_bet='Belgique', extra=None, user=u)
        with self.assertRaises(ValueError):
            with transaction.atomic():
                ExtraBet.objects.create(result_bet='Luxembourg', extra=e1, user=None)

    def test_invalid_fields(self):
        e, u = utils.create_extra(), utils.create_user()
        with self.assertRaises(DataError):
            with transaction.atomic():
                ExtraBet.objects.create(result_bet=51*'z', extra=e, user=u)

    def test_invalid_duplicates(self):
        e1, e2, u1, u2 = utils.create_extra(), utils.create_extra(), utils.create_user(), utils.create_user()
        ExtraBet.objects.create(result_bet='Polska', extra=e1, user=u1)
        ExtraBet.objects.create(result_bet='Polska', extra=e2, user=u2)
        ExtraBet.objects.create(result_bet='Polska', extra=e1, user=u2)
        ExtraBet.objects.create(result_bet='Polska', extra=e2, user=u1)

        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                ExtraBet.objects.create(result_bet='Romania', extra=e1, user=u2)

    def test_bet_str(self):
        u, g = utils.create_user(), utils.create_game()

        eb = utils.create_extrabet(result_bet='Suisse')
        self.assertEqual('Suisse', eb.bet_str())

        eb = utils.create_extrabet()
        self.assertEqual('---', eb.bet_str())

    def test_get_user_bets(self):
        u1, u2, u3 = utils.create_user(), utils.create_user(), utils.create_user()

        u1_bets = [utils.create_extrabet(user=u1) for i in range(1, 5)]
        u2_bets = [utils.create_extrabet(user=u2) for i in range(1, 3)]
        u3_bets = [utils.create_extrabet(user=u3) for i in range(1, 8)]

        self.assertEqual(13, len(ExtraBet.objects.all()))
        self.assertListEqual(u1_bets, list(ExtraBet.get_user_bets(u1.pk)))
        self.assertListEqual(u2_bets, list(ExtraBet.get_user_bets(u2.pk)))
        self.assertListEqual(u3_bets, list(ExtraBet.get_user_bets(u3.pk)))

    def test_get_extra_bets(self):
        e1, e2, e3 = utils.create_extra(), utils.create_extra(), utils.create_extra()

        e1_bets = [utils.create_extrabet(extra=e1) for i in range(1, 2)]
        e2_bets = [utils.create_extrabet(extra=e2) for i in range(1, 5)]
        e3_bets = [utils.create_extrabet(extra=e3) for i in range(1, 7)]

        self.assertEqual(11, len(ExtraBet.objects.all()))
        self.assertListEqual(e1_bets, list(ExtraBet.get_extra_bets(e1.pk)))
        self.assertListEqual(e2_bets, list(ExtraBet.get_extra_bets(e2.pk)))
        self.assertListEqual(e3_bets, list(ExtraBet.get_extra_bets(e3.pk)))

    def test_get_user_extra_bet(self):
        u1, u2 = utils.create_user(), utils.create_user()
        e1, e2 = utils.create_extra(), utils.create_extra()

        eb1 = utils.create_extrabet('', e1, u1)
        eb2 = utils.create_extrabet('', e2, u1)
        eb3 = utils.create_extrabet('', e1, u2)

        self.assertEqual(eb1, ExtraBet.get_user_extra_bet(u1.pk, e1.pk))
        self.assertEqual(eb2, ExtraBet.get_user_extra_bet(u1.pk, e2.pk))
        self.assertEqual(eb3, ExtraBet.get_user_extra_bet(u2.pk, e1.pk))
        self.assertIsNone(ExtraBet.get_user_extra_bet(u2.pk, e2.pk))

    def test_compute_points(self):
        u, e1, e2 = utils.create_user(), utils.create_extra(result=u'Österreich'), utils.create_extra(result='Espana')

        eb = utils.create_extrabet(u'Österreich', e1, u)
        self.assertEqual(10, eb.compute_points())

        eb = utils.create_extrabet(u'Deutschland', e2, u)
        self.assertEqual(0, eb.compute_points())

    def test_compute_points_none(self):
        u, e, e_r = utils.create_user(), utils.create_extra(), utils.create_extra(result=u'Österreich')

        # extra has no result
        eb1 = utils.create_extrabet(u'Österreich', e, u)
        self.assertEqual(0, eb1.compute_points())

        # no bet was set
        eb2 = utils.create_extrabet('', e_r, u)
        self.assertEqual(0, eb2.compute_points())


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
        print "~"*50
        print "SCALING test START = %s" % start_time

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

        avg_game_save = reduce(lambda x, y: x + y, game_save_times) / len(game_save_times)

        end_time = time.clock()
        duration = (end_time - start_time)
        print "SCALING test FINISHED = %s" % end_time
        print "TOOK %f s altogether" % duration
        print "TOOK %f s on average per game save" % avg_game_save
        print "~"*50
        print "~"*50

        print "USER STATISTICS:"
        ranked_users = sorted(list(User.objects.all().order_by('username')),
                              key=lambda it: (it.statistic.points, it.statistic.no_volltreffer, it.statistic.no_bets),
                              reverse=True)
        for u in ranked_users:
            print u.statistic.pretty_print()

        self.assertEqual(int(BET_AMOUNT*len(games)), users[0].statistic.no_bets)
        # TODO what else could be asserted?


class ProfileTests(TestCase):

    def test_to_string(self):
        u = utils.create_user('Queen')
        p = Profile.objects.get(user=u)

        self.assertEqual("Queen's Profile", str(p))

    def test_ordering(self):
        # TODO case-insensitive ordering does not work with Meta class
        u1, u2, u3 = utils.create_user('Tick'), utils.create_user('zack'), utils.create_user('Track')

        profiles = list(Profile.objects.all())
        self.assertListEqual([u1, u2, u3], [p.user for p in profiles])

    def test_invalid_missing_fields(self):
        with self.assertRaises(ValueError):
            with transaction.atomic():
                Profile.objects.create(user=None)

    def test_create_profile_after_user(self):
        User.objects.create(username='fipsy', first_name='John', last_name='Doe')
        user = User.objects.get(username='fipsy')
        self.assertEqual('fipsy', user.username)
        self.assertIsNotNone(user.profile)

        profile = Profile.objects.get(user__username='fipsy')
        self.assertIsNotNone(profile)
        self.assertEqual(user, profile.user)
        self.assertEqual(profile, user.profile)
        self.assertEqual('John', profile.user.first_name)
        self.assertEqual('Doe', profile.user.last_name)

    def test_get_display_name(self):
        User.objects.create(username='fipsy', first_name='John', last_name='Doe')
        profile = Profile.objects.get(user__username='fipsy')
        self.assertEqual('John Doe', profile.get_display_name())

        User.objects.create(username='fapsy')
        profile = Profile.objects.get(user__username='fapsy')
        self.assertEqual('fapsy', profile.get_display_name())

    def test_calculate_statistics(self):
        # TODO
        pass


class PostTests(TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        Post.objects.all().delete()
        utils.cleanup()

    def test_to_string(self):
        u = utils.create_user('the queen')
        p = Post.objects.create(content='Tolle Neuigkeiten!', author=u)
        self.assertEqual('Post by the queen', str(p))

    def test_invalid_missing_fields(self):
        u = utils.create_user()
        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                Post.objects.create(content=None, author=u)
        with self.assertRaises(ValidationError):
            with transaction.atomic():
                Post.objects.create(content='', author=u).clean()

    def test_date_created(self):
        p = utils.create_post()
        date_format = '%d-%m-%y %H:%M:%S'
        self.assertTrue(p.date_created.strftime(date_format) == timezone.now().strftime(date_format))

        # auto_now_add can *not* be overriden!
        other_time = utils.create_datetime_from_now(timedelta(days=2, hours=1))
        p = Post.objects.create(content='foo', author=utils.create_user(), date_created=other_time)
        self.assertTrue(p.date_created.strftime(date_format) == timezone.now().strftime(date_format))