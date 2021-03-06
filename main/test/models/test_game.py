# -*- coding: utf-8 -*-
from datetime import timedelta

from django.core.exceptions import ValidationError
from django.db import transaction
from django.db.utils import IntegrityError
from django.test import TestCase
from django.utils import timezone

from main.models import Game, Team, Bettable
from main.test.utils import TestModelUtils as utils


class GameTests(TestCase):

    def setUp(self):
        Bettable.objects.all().delete()
        Game.objects.all().delete()
        Team.objects.all().delete()

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

        # these should be OK, because the teams are either in the same group or it's a knockout round
        Game.objects.create(kickoff=now, deadline=now, hometeam=t1, awayteam=t3, venue=v1, round=r1).clean()
        Game.objects.create(kickoff=now, deadline=now, hometeam=t1, awayteam=t2, venue=v1, round=r2).clean()

        # this game is not allowed, because the round should be a non knockout round but the teams are not in the
        # same group
        g1 = Game.objects.create(kickoff=now, deadline=now, hometeam=t2, awayteam=t3, venue=v1, round=r1)
        self.assertRaises(ValidationError, g1.clean)

    def test_result_str(self):
        g1_result = utils.create_game(homegoals=4, awaygoals=2)
        g2_noresult = utils.create_game(homegoals=-1, awaygoals=-1)

        self.assertEqual('4:2', g1_result.result_str())
        self.assertIsNone(g2_noresult.result_str())

    def test_has_started(self):
        now = timezone.now()
        g1 = utils.create_game(kickoff=now)
        g2 = utils.create_game(kickoff=now + timedelta(seconds=-1))
        g3 = utils.create_game(kickoff=now + timedelta(seconds=1))
        g4 = utils.create_game(kickoff=now + timedelta(hours=2))

        self.assertTrue(g1.has_started())
        self.assertTrue(g2.has_started())
        self.assertFalse(g3.has_started())
        self.assertFalse(g4.has_started())

    def test_is_over(self):
        now = timezone.now()
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

    def test_get_latest_finished_game(self):
        now = timezone.now()
        g1 = utils.create_game(kickoff=now + timedelta(days=-3), homegoals=3, awaygoals=1)
        g2 = utils.create_game(kickoff=now + timedelta(days=-2), homegoals=4, awaygoals=0)
        g3 = utils.create_game(kickoff=now + timedelta(days=-1))
        g4 = utils.create_game(kickoff=now)
        g5 = utils.create_game(kickoff=now + timedelta(days=3))

        self.assertEqual(g2, Game.get_latest_finished_game())

    def test_get_first_game(self):
        now = timezone.now()
        g1 = utils.create_game(kickoff=now)
        g2 = utils.create_game(kickoff=now + timedelta(seconds=-1))
        g3 = utils.create_game(kickoff=now + timedelta(seconds=1))
        g4 = utils.create_game(kickoff=now + timedelta(hours=2))

        self.assertEqual(g2, Game.get_first_game())

    def test_two_identical_games_in_same_round_should_be_forbidden(self):
        # GIVEN: a round
        now = utils.create_datetime_from_now()
        a_round = utils.create_round('My Round')

        # AND: two teams
        t1 = utils.create_team('Team 1', 'TM1')
        t2 = utils.create_team('Team 2', 'TM2')

        # AND: a game in the given round
        utils.create_game(hometeam=t1, awayteam=t2, round=a_round)

        # WHEN: the same game is created again in the same round
        # THEN: an IntegrityError should be raised
        with self.assertRaises(IntegrityError):
            utils.create_game(hometeam=t1, awayteam=t2, round=a_round)

    def test_two_identical_games_in_different_rounds_should_be_allowed(self):
        # GIVEN: two rounds
        vor, af = utils.create_round('Vorrunde'), utils.create_round('Achtelfinale', True)

        # AND: two teams
        t1 = utils.create_team('Team 1', 'TM1')
        t2 = utils.create_team('Team 2', 'TM2')

        # AND: a game in the Vorrunde
        g1 = utils.create_game(hometeam=t1, awayteam=t2, round=vor)

        # WHEN: the same game is created in a different round
        g2 = utils.create_game(hometeam=t1, awayteam=t2, round=af)

        # THEN: no error should occur and both games should have been created
        self.assertIsNotNone(Game.objects.get(pk=g1.pk))
        self.assertEqual(vor, Game.objects.get(pk=g1.pk).round)

        self.assertIsNotNone(Game.objects.get(pk=g2.pk))
        self.assertEqual(af, Game.objects.get(pk=g2.pk).round)
