# -*- coding: utf-8 -*-

from rest_framework import status

from main.models import TournamentGroup, Team
from main.test.api.abstract_rtg_api_test import RtgApiTestCase
from main.test.api.test_tournament_group import TournamentGroupApiTests


class TeamApiTests(RtgApiTestCase):

    def tearDown(self):
        self.delete_test_team()
        TournamentGroupApiTests.delete_test_group()

    def test_team_create(self):
        self.create_test_user(admin=True)
        response = self.create_test_team_api()
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Team.objects.count(), 1)
        self.assertIsNotNone(Team.objects.get(abbreviation='RFC'))

    def test_team_create_unauth(self):
        self.create_test_user()
        response = self.create_test_team_api()
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_team_read(self):
        self.create_test_user()
        response = self.get_test_team_api()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Team.objects.count(), 1)
        self.assertIsNotNone(Team.objects.get(abbreviation='RFC'))

    def test_team_public_read(self):
        self.create_test_user(auth=False)
        response = self.get_test_team_api()
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_team_update(self):
        self.create_test_user(admin=True)
        response = self.update_test_team_api()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Team.objects.count(), 1)
        self.assertIsNotNone(Team.objects.get(name='GNTT Brothers 08'))
        self.assertRaises(Team.DoesNotExist, Team.objects.get, abbreviation='RFC')

    def test_team_update_unauth(self):
        self.create_test_user()
        response = self.update_test_team_api()
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_team_delete(self):
        self.create_test_user(admin=True)
        response = self.delete_test_team_api()
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Team.objects.count(), 0)

    def test_team_delete_unauth(self):
        self.create_test_user()
        response = self.delete_test_team_api()
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_team_delete_public(self):
        self.create_test_user(auth=False)
        response = self.delete_test_team_api()
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    @staticmethod
    def create_test_team():
        try:
            test_team = Team.objects.get(name='RTG United FC')
        except Team.DoesNotExist:
            test_group = TournamentGroupApiTests.create_test_group()
            test_team = Team(name='RTG United FC', abbreviation='RFC', group=test_group)
            test_team.save()
        return test_team

    @staticmethod
    def delete_test_team():
        try:
            test_team = Team.objects.get(name='RTG United FC')
            test_team.delete()
        except Team.DoesNotExist:
            pass

    def get_test_team_api(self):
        self.create_test_team()
        team_pk = Team.objects.get(abbreviation='RFC').pk
        return self.client.get('%s%i/' % (self.TEAMS_BASEURL, team_pk))

    def create_test_team_api(self):
        test_group = TournamentGroupApiTests.create_test_group()
        return self.client.post(self.TEAMS_BASEURL, {'name': 'RTG United FC', 'abbreviation': 'RFC',
                                                     'group': test_group.pk}, format='json')

    def update_test_team_api(self):
        self.create_test_team()
        group_pk = TournamentGroup.objects.get(abbreviation='TGR').pk
        team_pk = Team.objects.get(abbreviation='RFC').pk
        return self.client.put("%s%i/" % (self.TEAMS_BASEURL, team_pk),
                               {'name': 'GNTT Brothers 08', 'abbreviation': 'GBR', 'group': group_pk}, format='json')

    def delete_test_team_api(self):
        self.create_test_team()
        team_pk = Team.objects.get(abbreviation='RFC').pk
        return self.client.delete("%s%i/" % (self.TEAMS_BASEURL, team_pk))