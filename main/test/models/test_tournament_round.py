# -*- coding: utf-8 -*-

from django.db import transaction, DataError
from django.db.utils import IntegrityError
from django.test import TestCase

from main.models import TournamentRound
from main.test.utils import TestModelUtils as utils


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
