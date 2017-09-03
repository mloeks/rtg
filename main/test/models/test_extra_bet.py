# -*- coding: utf-8 -*-

from django.db import transaction, DataError
from django.db.utils import IntegrityError
from django.test import TestCase

from main.models import ExtraBet
from main.test.utils import TestModelUtils as utils


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
        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                ExtraBet.objects.create(result_bet='Belgique', extra=None, user=u)
        with self.assertRaises(IntegrityError):
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
        u, e1, e2 = utils.create_user(), utils.create_extra(result='Österreich'), utils.create_extra(result='Espana')

        eb = utils.create_extrabet('Österreich', e1, u)
        self.assertEqual(10, eb.compute_points())

        eb = utils.create_extrabet('Deutschland', e2, u)
        self.assertEqual(0, eb.compute_points())

    def test_compute_points_none(self):
        u, e, e_r = utils.create_user(), utils.create_extra(), utils.create_extra(result='Österreich')

        # extra has no result
        eb1 = utils.create_extrabet('Österreich', e, u)
        self.assertEqual(0, eb1.compute_points())

        # no bet was set
        eb2 = utils.create_extrabet('', e_r, u)
        self.assertEqual(0, eb2.compute_points())