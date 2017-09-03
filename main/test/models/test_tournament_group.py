# -*- coding: utf-8 -*-

from django.db import transaction, DataError
from django.db.utils import IntegrityError
from django.test import TestCase

from main.models import TournamentGroup
from main.test.utils import TestModelUtils as utils


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
