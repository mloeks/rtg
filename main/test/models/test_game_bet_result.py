# -*- coding: utf-8 -*-

from django.db import transaction, DataError
from django.db.utils import IntegrityError
from django.test import TestCase

from main.models import GameBetResult
from main.test.utils import TestModelUtils as utils


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