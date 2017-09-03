# -*- coding: utf-8 -*-

from rest_framework import status

from main.models import Game
from main.test.api.abstract_rtg_api_test import RtgApiTestCase
from main.test.api.test_team import TeamApiTests
from main.test.api.test_tournament_round import TournamentRoundApiTests
from main.test.api.test_venue import VenueApiTests
from main.test.utils import TestModelUtils


class GameApiTests(RtgApiTestCase):

    def tearDown(self):
        Game.objects.all().delete()

    def test_game_create(self):
        self.create_test_user(admin=True)
        response = self.create_test_game_api('RTG National Stadium')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Game.objects.count(), 1)
        self.assertIsNotNone(Game.objects.get(venue__name='RTG National Stadium'))

    def test_game_create_unauth(self):
        self.create_test_user()
        response = self.create_test_game_api()
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_game_read(self):
        self.create_test_user()
        response = self.get_test_game_api('RTG National Stadium')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Game.objects.count(), 1)
        self.assertIsNotNone(Game.objects.get(venue__name='RTG National Stadium'))

    def test_game_public_read(self):
        self.create_test_user(auth=False)
        response = self.get_test_game_api()
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_game_update(self):
        self.create_test_user(admin=True)
        response = self.update_test_game_api()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Game.objects.count(), 1)

        stored_game = list(Game.objects.all()[:1])[0]
        self.assertIsNotNone(stored_game)
        self.assertEquals(stored_game.homegoals, 3)
        self.assertEquals(stored_game.awaygoals, 2)
        self.assertRaises(Game.DoesNotExist, Game.objects.get, kickoff='2016-06-06 18:00:00+0000')

    def test_game_update_unauth(self):
        self.create_test_user()
        response = self.update_test_game_api()
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_game_delete(self):
        self.create_test_user(admin=True)
        response = self.delete_test_game_api()
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Game.objects.count(), 0)

    def test_game_delete_unauth(self):
        self.create_test_user()
        response = self.delete_test_game_api()
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_game_delete_public(self):
        self.create_test_user(auth=False)
        response = self.delete_test_game_api()
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    @staticmethod
    def create_test_game(venue_name=None):
        team_1 = TestModelUtils.create_team()
        team_2 = TestModelUtils.create_team()
        test_venue = TestModelUtils.create_venue(venue_name)
        test_round = TestModelUtils.create_round()
        # TODO deadline should not be required, but apparently is
        test_game = Game(kickoff='2016-06-06 18:00:00+0000', deadline='2016-06-06 18:00:00+0000',
                         hometeam=team_1, awayteam=team_2, venue=test_venue, round=test_round)
        test_game.save()
        return test_game

    def get_test_game_api(self, venue_name=None):
        test_game = self.create_test_game(venue_name)
        return self.client.get('%s%i/' % (self.GAMES_BASEURL, test_game.pk))

    def create_test_game_api(self, venue_name=None):
        team_1 = TestModelUtils.create_team()
        team_2 = TestModelUtils.create_team()
        test_venue = TestModelUtils.create_venue(venue_name)
        test_round = TestModelUtils.create_round()
        return self.client.post(self.GAMES_BASEURL, {'kickoff': '2016-06-06 18:00:00+0000',
                                                     'deadline': '2016-06-06 18:00:00+0000',
                                                     'hometeam': team_1.pk, 'awayteam': team_2.pk,
                                                     'venue': test_venue.pk, 'round': test_round.pk}, format='json')

    def update_test_game_api(self):
        test_game = self.create_test_game()
        team_1 = TeamApiTests.create_test_team()
        team_2 = TeamApiTests.create_test_team()
        test_venue = VenueApiTests.create_test_venue()
        test_round = TournamentRoundApiTests.create_test_round()
        return self.client.put("%s%i/" % (self.GAMES_BASEURL, test_game.pk),
                               {'kickoff': '2016-06-08 20:45:30+0000', 'deadline': '2016-06-06 18:00:00+0000',
                                'hometeam': team_1.pk, 'awayteam': team_2.pk, 'venue': test_venue.pk,
                                'round': test_round.pk, 'homegoals': 3, 'awaygoals': 2}, format='json')

    def delete_test_game_api(self):
        test_game = self.create_test_game()
        return self.client.delete("%s%i/" % (self.GAMES_BASEURL, test_game.pk))