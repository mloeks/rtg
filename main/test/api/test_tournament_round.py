# -*- coding: utf-8 -*-

from rest_framework import status

from main.models import TournamentRound
from main.test.api.abstract_rtg_api_test import RtgApiTestCase


class TournamentRoundApiTests(RtgApiTestCase):

    def tearDown(self):
        self.delete_test_round()

    def test_round_create(self):
        self.create_test_user(admin=True)
        response = self.create_test_round_api()
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(TournamentRound.objects.count(), 1)
        self.assertIsNotNone(TournamentRound.objects.get(abbreviation='TRU'))

    def test_round_create_unauth(self):
        self.create_test_user()
        response = self.create_test_round_api()
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_round_read(self):
        self.create_test_user()
        response = self.get_test_round_api()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(TournamentRound.objects.count(), 1)
        self.assertIsNotNone(TournamentRound.objects.get(abbreviation='TRU'))

    def test_round_public_read(self):
        self.create_test_user(auth=False)
        response = self.get_test_round_api()
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_round_update(self):
        self.create_test_user(admin=True)
        response = self.update_test_round_api()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(TournamentRound.objects.count(), 1)
        self.assertIsNotNone(TournamentRound.objects.get(name='Andere Runde'))
        self.assertRaises(TournamentRound.DoesNotExist, TournamentRound.objects.get, abbreviation='TRU')

    def test_round_update_unauth(self):
        self.create_test_user()
        response = self.update_test_round_api()
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_round_delete(self):
        self.create_test_user(admin=True)
        response = self.delete_test_round_api()
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(TournamentRound.objects.count(), 0)

    def test_round_delete_unauth(self):
        self.create_test_user()
        response = self.delete_test_round_api()
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_round_delete_public(self):
        self.create_test_user(auth=False)
        response = self.delete_test_round_api()
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    @staticmethod
    def create_test_round():
        try:
            test_round = TournamentRound.objects.get(name='Testrunde')
        except TournamentRound.DoesNotExist:
            test_round = TournamentRound(name='Testrunde', is_knock_out=True, display_order=123, abbreviation='TRU')
            test_round.save()
        return test_round

    @staticmethod
    def delete_test_round():
        try:
            test_round = TournamentRound.objects.get(name='Testrunde')
            test_round.delete()
        except TournamentRound.DoesNotExist:
            pass

    def get_test_round_api(self):
        self.create_test_round()
        round_pk = TournamentRound.objects.get(abbreviation='TRU').pk
        return self.client.get('%s%i/' % (self.ROUNDS_BASEURL, round_pk))

    def create_test_round_api(self):
        return self.client.post(self.ROUNDS_BASEURL, {'name': 'Testrunde', 'is_knock_out': True, 'display_order': 123,
                                                      'abbreviation': 'TRU'}, format='json')

    def update_test_round_api(self):
        self.create_test_round()
        round_pk = TournamentRound.objects.get(abbreviation='TRU').pk
        return self.client.put("%s%i/" % (self.ROUNDS_BASEURL, round_pk),
                               {'name': 'Andere Runde', 'is_knock_out': False, 'display_order': 456,
                                'abbreviation': 'AR'}, format='json')

    def delete_test_round_api(self):
        self.create_test_round()
        round_pk = TournamentRound.objects.get(abbreviation='TRU').pk
        return self.client.delete("%s%i/" % (self.ROUNDS_BASEURL, round_pk))