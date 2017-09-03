# -*- coding: utf-8 -*-

from django.db import transaction, DataError
from django.db.utils import IntegrityError
from django.test import TestCase

from main.models import Venue
from main.test.utils import TestModelUtils as utils


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
                Venue.objects.create(name='Südstadion', city=None, capacity=456)
        # capacity is optional
        Venue.objects.create(name=u"1. FC Köln", city='Köln')

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