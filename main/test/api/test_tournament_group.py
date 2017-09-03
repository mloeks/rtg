# -*- coding: utf-8 -*-
from rest_framework import status

from main.models import TournamentGroup
from main.test.api.abstract_rtg_api_test import RtgApiTestCase


class TournamentGroupApiTests(RtgApiTestCase):

    def tearDown(self):
        self.delete_test_group()

    def test_group_create(self):
        self.create_test_user(admin=True)
        response = self.create_test_group_api()
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(TournamentGroup.objects.count(), 1)
        self.assertIsNotNone(TournamentGroup.objects.get(abbreviation='HGR'))

    def test_group_create_unauth(self):
        self.create_test_user()
        response = self.create_test_group_api()
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_group_read(self):
        self.create_test_user()
        response = self.get_test_group_api()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(TournamentGroup.objects.count(), 1)
        self.assertIsNotNone(TournamentGroup.objects.get(abbreviation='TGR'))

    def test_group_public_read(self):
        self.create_test_user(auth=False)
        response = self.get_test_group_api()
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_group_update(self):
        self.create_test_user(admin=True)
        response = self.update_test_group_api()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(TournamentGroup.objects.count(), 1)
        self.assertIsNotNone(TournamentGroup.objects.get(name='Andere Gruppe'))
        self.assertRaises(TournamentGroup.DoesNotExist, TournamentGroup.objects.get, abbreviation='TGR')

    def test_group_update_unauth(self):
        self.create_test_user()
        response = self.update_test_group_api()
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_group_delete(self):
        self.create_test_user(admin=True)
        response = self.delete_test_group_api()
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(TournamentGroup.objects.count(), 0)

    def test_group_delete_unauth(self):
        self.create_test_user()
        response = self.delete_test_group_api()
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_group_delete_public(self):
        self.create_test_user(auth=False)
        response = self.delete_test_group_api()
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    @staticmethod
    def create_test_group():
        try:
            test_group = TournamentGroup.objects.get(name='test_group')
        except TournamentGroup.DoesNotExist:
            test_group = TournamentGroup(name='test_group', abbreviation='TGR')
            test_group.save()
        return test_group

    @staticmethod
    def delete_test_group():
        try:
            test_group = TournamentGroup.objects.get(name='test_group')
            test_group.delete()
        except TournamentGroup.DoesNotExist:
            pass

    def get_test_group_api(self):
        self.create_test_group()
        group_pk = TournamentGroup.objects.get(abbreviation='TGR').pk
        return self.client.get('%s%i/' % (self.GROUPS_BASEURL, group_pk))

    def create_test_group_api(self):
        return self.client.post(self.GROUPS_BASEURL, {'name': 'Hammergruppe', 'abbreviation': 'HGR'}, format='json')

    def update_test_group_api(self):
        self.create_test_group()
        group_pk = TournamentGroup.objects.get(abbreviation='TGR').pk
        return self.client.put("%s%i/" % (self.GROUPS_BASEURL, group_pk),
                               {'name': 'Andere Gruppe', 'abbreviation': 'AGR'}, format='json')

    def delete_test_group_api(self):
        self.create_test_group()
        group_pk = TournamentGroup.objects.get(abbreviation='TGR').pk
        return self.client.delete("%s%i/" % (self.GROUPS_BASEURL, group_pk))