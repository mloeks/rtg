# -*- coding: utf-8 -*-
from datetime import timedelta

from django.db import transaction, DataError
from django.db.utils import IntegrityError
from django.test import TestCase
from django.utils import timezone

from main.models import Extra
from main.test.utils import TestModelUtils as utils


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

    def test_invalid_fields(self):
        with self.assertRaises(DataError):
            with transaction.atomic():
                Extra.objects.create(name=51*'z', deadline=timezone.now())
        with self.assertRaises(DataError):
            with transaction.atomic():
                Extra.objects.create(name='RTG-Meister', deadline=timezone.now(), result=51*'y')

    def test_has_result(self):
        e1, e2 = utils.create_extra(), utils.create_extra(result='Die Königin!')

        self.assertFalse(e1.has_result())
        self.assertTrue(e2.has_result())

    def test_deadline_passed(self):
        now = utils.create_datetime_from_now()
        self.assertTrue(utils.create_extra().deadline_passed())
        self.assertTrue(utils.create_extra(deadline=now + timedelta(hours=-2)).deadline_passed())
        self.assertFalse(utils.create_extra(deadline=now + timedelta(hours=2)).deadline_passed())

    # TODO P3 move to Bettable test
    # def test_get_finished_extras(self):
    #     e1, e2, e3 = utils.create_extra(result='Die Königin!'), utils.create_extra(), \
    #                  utils.create_extra(result='Der Prinzgemahl!')
    #
    #     self.assertListEqual([e1, e3], list(Extra.get_finished_extras()))