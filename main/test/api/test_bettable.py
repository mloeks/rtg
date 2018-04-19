# -*- coding: utf-8 -*-
from datetime import timedelta, datetime

from django.contrib.auth.models import User
from rest_framework import status

from main.models import Bet, Bettable
from main.test.api.abstract_rtg_api_test import RtgApiTestCase
from main.test.utils import TestModelUtils


class BettableApiTests(RtgApiTestCase):

    def setUp(self):
        User.objects.all().delete()
        Bettable.objects.all().delete()
        Bet.objects.all().delete()

    def test_read_mixed_bettables(self):
        self.create_test_user()

        some_game = TestModelUtils.create_game(deadline=datetime.now())
        some_extra = TestModelUtils.create_extra(deadline=datetime.now() + timedelta(days=1))

        response = self.client.get(self.BETTABLES_BASEURL)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(2, len(response.data))
        self.assertEqual(some_game.bettable_ptr.name, response.data[0]['name'])
        self.assertEqual('game', response.data[0]['type'])
        self.assertEqual(some_extra.name, response.data[1]['name'])
        self.assertEqual('extra', response.data[1]['type'])

    # TODO it would be more RESTful if the modifying requests tested below returned 405 (Method Not Allowed) instead
    # of 401 (Unauthorized) - since this should have nothing to do with authentication. The bettable resource should
    # just not offer write methods.
    # (I thought that would be the case with ReadOnlyModelViewSet, but apparently it's not)

    def test_bettables_must_not_be_createable(self):
        response = self.client.post(self.BETTABLES_BASEURL, {'name': 'a bettable', 'deadline': datetime.now()}, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_bettables_must_not_be_updateable(self):
        some_bettable = TestModelUtils.create_game()
        response = self.client.put('%s%i/' % (self.BETTABLES_BASEURL, some_bettable.pk),
                                   {'name': 'a new bettable', 'deadline': datetime.now() + timedelta(days=1)},
                                   format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_bettables_must_not_be_deleteable(self):
        some_bettable = TestModelUtils.create_game()
        response = self.client.delete('%s%i/' % (self.BETTABLES_BASEURL, some_bettable.pk))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
