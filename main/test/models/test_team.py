# -*- coding: utf-8 -*-

from django.db import transaction, DataError
from django.db.utils import IntegrityError
from django.test import TestCase

from main.models import Team
from main.test.utils import TestModelUtils as utils


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