# -*- coding: utf-8 -*-
from django.test import TestCase

from main.models import Bet, Bettable, Extra
from main.test.utils import TestModelUtils


class ExtraResultBetUpdateTests(TestCase):

    def tearDown(self):
        Bettable.objects.all().delete()
        Extra.objects.all().delete()
        Bet.objects.all().delete()

    def test_new_extra_result_updates_bettable(self):
        # GIVEN: some extra
        some_extra = TestModelUtils.create_extra()

        # WHEN: the extra gets a result
        some_extra.result = 'a result'
        some_extra.save()

        # THEN: the parent bettable should have this result set
        self.assertEqual('a result', Bettable.objects.get(pk=some_extra.pk).result)

    def test_new_extra_result_updates_bet(self):
        # GIVEN: some extra
        some_extra = TestModelUtils.create_extra()

        # AND: some bet on this extra
        some_bet = TestModelUtils.create_bet(bettable=some_extra, result_bet="my result")

        # WHEN: the extra gets a result
        some_extra.result = 'my result'
        some_extra.save()

        # THEN: the bet should have the correct points
        updated_bet = Bet.objects.get(pk=some_bet.pk)
        self.assertEqual(10, updated_bet.points)
        self.assertEqual('volltreffer', updated_bet.result_bet_type)

    def test_remove_extra_result_resets_bettable(self):
        # WHEN: some extra with a result is created
        some_extra = TestModelUtils.create_extra(result='Gewinner')

        # THEN: the corresponding bettable should have that result set
        self.assertEquals("Gewinner", Bettable.objects.get(pk=some_extra.pk).result)

        # WHEN: the extra's result is reset
        some_extra.result = None
        some_extra.save()

        # THEN: the bettable's result should be None
        self.assertIsNone(Bettable.objects.get(pk=some_extra.pk).result)

    def test_remove_extra_result_resets_bet_points(self):
        # GIVEN: some game with a result
        some_extra = TestModelUtils.create_extra(result="result")

        # AND: some bet with points
        some_bet = TestModelUtils.create_bet(bettable=some_extra, result_bet="result")
        some_bet.points = 4711
        some_bet.save()

        # WHEN: the extra's result is reset
        some_extra.result = None
        some_extra.save()

        # THEN: the bet should reset it's points to None (not 0)
        updated_bet = Bet.objects.get(pk=some_bet.pk)
        self.assertIsNone(updated_bet.points)
        self.assertNotEqual(0, updated_bet.points)
