# -*- coding: utf-8 -*-

from django.db import transaction, DataError
from django.db.utils import IntegrityError
from django.test import TestCase

from main.models import ExtraChoice
from main.test.utils import TestModelUtils as utils


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
        with self.assertRaises(IntegrityError):
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