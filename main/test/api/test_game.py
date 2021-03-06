# -*- coding: utf-8 -*-
from datetime import timedelta

from django.utils import timezone
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
        test_game = TestModelUtils.create_game()
        response = self.get_test_game_api(test_game.pk)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Game.objects.count(), 1)
        self.assertIsNotNone(Game.objects.get(venue__name=test_game.venue.name))

    def test_game_response_schema(self):
        self.create_test_user()
        test_game = TestModelUtils.create_game()
        response = self.get_test_game_api(test_game.pk).data

        self.assertTrue('round_details' in response and 'abbreviation' in response['round_details'])
        self.assertTrue('round_details' in response and 'name' in response['round_details'])
        self.assertTrue('round_details' in response and 'is_knock_out' in response['round_details'])
        self.assertTrue('city' in response)
        self.assertTrue('bets_open' in response)

        self.assertFalse('venue' in response)
        self.assertFalse('round' in response)

    def test_game_public_read(self):
        self.create_test_user(auth=False)
        test_game = TestModelUtils.create_game()
        response = self.get_test_game_api(test_game.pk)
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

    def test_game_update_result(self):
        self.create_test_user(admin=True)
        g1 = TestModelUtils.create_game()
        self.assertEqual(Game.objects.count(), 1)

        self.client.patch("%s%i/" % (self.GAMES_BASEURL, g1.pk), {'homegoals': 3, 'awaygoals': 2}, format='json')

        stored_game = list(Game.objects.all()[:1])[0]
        self.assertEquals(stored_game.homegoals, 3)
        self.assertEquals(stored_game.awaygoals, 2)

    def test_game_update_unauth(self):
        self.create_test_user()
        response = self.update_test_game_api()
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_game_delete(self):
        self.create_test_user(admin=True)
        test_game = TestModelUtils.create_game()
        response = self.delete_test_game_api(test_game.pk)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Game.objects.count(), 0)

    def test_game_delete_unauth(self):
        self.create_test_user()
        test_game = TestModelUtils.create_game()
        response = self.delete_test_game_api(test_game.pk)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_game_delete_public(self):
        self.create_test_user(auth=False)
        test_game = TestModelUtils.create_game()
        response = self.delete_test_game_api(test_game.pk)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_game_filter_from_date(self):
        self.create_test_user()
        now = timezone.now()

        g1 = TestModelUtils.create_game(kickoff=now - timedelta(days=5))
        g2 = TestModelUtils.create_game(kickoff=now - timedelta(hours=3))
        g3 = TestModelUtils.create_game(kickoff=now)
        g4 = TestModelUtils.create_game(kickoff=now + timedelta(hours=2))

        response = self.client.get(self.GAMES_BASEURL, {'from': now})
        self.assertEqual(2, response.data['count'])
        self.assertEqual(g3.id, response.data['results'][0]['id'])
        self.assertEqual(g4.id, response.data['results'][1]['id'])

    def test_game_filter_bets_open(self):
        self.create_test_user()
        now = timezone.now()

        g1 = TestModelUtils.create_game(deadline=now - timedelta(days=5))
        g2 = TestModelUtils.create_game(deadline=now - timedelta(hours=3))
        g3 = TestModelUtils.create_game(deadline=now)
        g4 = TestModelUtils.create_game(deadline=now + timedelta(hours=2))

        response = self.client.get(self.GAMES_BASEURL, {'bets_open': 'true'})
        self.assertEqual(1, response.data['count'])
        self.assertEqual(g4.id, response.data['results'][0]['id'])

    def test_game_filter_bets_not_open(self):
        self.create_test_user()
        now = timezone.now()

        g1 = TestModelUtils.create_game(deadline=now - timedelta(days=5))
        g2 = TestModelUtils.create_game(deadline=now - timedelta(hours=3))
        g3 = TestModelUtils.create_game(deadline=now)
        g4 = TestModelUtils.create_game(deadline=now + timedelta(hours=2))

        response = self.client.get(self.GAMES_BASEURL, {'bets_open': 'false'})
        self.assertEqual(3, response.data['count'])
        self.assertEqual(g1.id, response.data['results'][0]['id'])
        self.assertEqual(g2.id, response.data['results'][1]['id'])
        self.assertEqual(g3.id, response.data['results'][2]['id'])

    def test_game_filter_kicked_off(self):
        self.create_test_user()
        now = timezone.now()

        g1 = TestModelUtils.create_game(kickoff=now - timedelta(days=5))
        g2 = TestModelUtils.create_game(kickoff=now - timedelta(hours=3))
        g3 = TestModelUtils.create_game(kickoff=now)
        g4 = TestModelUtils.create_game(kickoff=now + timedelta(hours=2))

        response = self.client.get(self.GAMES_BASEURL, {'kicked_off': 'true'})
        self.assertEqual(3, response.data['count'])
        self.assertEqual(g1.id, response.data['results'][0]['id'])
        self.assertEqual(g2.id, response.data['results'][1]['id'])
        self.assertEqual(g3.id, response.data['results'][2]['id'])

    def get_test_game_api(self, game_id):
        return self.client.get('%s%i/' % (self.GAMES_BASEURL, game_id))

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
        test_game = TestModelUtils.create_game()
        team_1 = TeamApiTests.create_test_team()
        team_2 = TeamApiTests.create_test_team()
        test_venue = VenueApiTests.create_test_venue()
        test_round = TournamentRoundApiTests.create_test_round()
        return self.client.put("%s%i/" % (self.GAMES_BASEURL, test_game.pk),
                               {'kickoff': '2016-06-08 20:45:30+0000', 'deadline': '2016-06-06 18:00:00+0000',
                                'hometeam': team_1.pk, 'awayteam': team_2.pk, 'venue': test_venue.pk,
                                'round': test_round.pk, 'homegoals': 3, 'awaygoals': 2}, format='json')

    def delete_test_game_api(self, game_id):
        return self.client.delete("%s%i/" % (self.GAMES_BASEURL, game_id))