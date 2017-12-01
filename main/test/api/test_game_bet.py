# -*- coding: utf-8 -*-
import json
from datetime import timedelta

from rest_framework import status

from main.models import GameBet
from main.test.api.abstract_rtg_api_test import RtgApiTestCase
from main.test.api.test_game import GameApiTests
from main.test.utils import TestModelUtils


class GameBetApiTests(RtgApiTestCase):

    def tearDown(self):
        pass

    def test_gamebet_create_admin(self):
        self.create_test_user(admin=True)
        response = self.create_test_gamebet_api()
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(GameBet.objects.count(), 1)
        self.assertIsNotNone(GameBet.objects.get(homegoals=5))

    def test_gamebet_create(self):
        u1 = TestModelUtils.create_user()
        self.create_test_user(u1.username)
        response = self.create_test_gamebet_api()
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(GameBet.objects.count(), 1)
        self.assertIsNotNone(GameBet.objects.get(homegoals=5))
        self.assertEqual(u1.pk, GameBet.objects.get(homegoals=5).user.id)

    def test_gamebet_create_public(self):
        self.create_test_user(auth=False)
        response = self.create_test_gamebet_api()
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_gamebet_read(self):
        # TODO apply restrictions when trying to read bets created by other users
        self.create_test_user()
        response = self.get_test_gamebet_api()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(GameBet.objects.count(), 1)
        self.assertIsNotNone(GameBet.objects.get(homegoals=4))

    def test_gamebet_read_allowed_filtered(self):
        u1, u2 = TestModelUtils.create_user(), TestModelUtils.create_user()

        g1 = TestModelUtils.create_game(kickoff=TestModelUtils.create_datetime_from_now(timedelta(days=-2)))
        g2 = TestModelUtils.create_game(deadline=TestModelUtils.create_datetime_from_now(timedelta(days=-1)))
        g3 = TestModelUtils.create_game(kickoff=TestModelUtils.create_datetime_from_now(timedelta(hours=5)))
        g4 = TestModelUtils.create_game(kickoff=TestModelUtils.create_datetime_from_now(timedelta(hours=8)),
                                        deadline=TestModelUtils.create_datetime_from_now(timedelta(hours=-1)))
        g5 = TestModelUtils.create_game(kickoff=TestModelUtils.create_datetime_from_now(timedelta(days=12)))

        gb1 = TestModelUtils.create_bet(u1, g1, 2, 1)
        gb2 = TestModelUtils.create_bet(u1, g2, 0, 1)
        gb3 = TestModelUtils.create_bet(u1, g3, 1, 3)
        gb4 = TestModelUtils.create_bet(u1, g5, 1, 3)

        gb5 = TestModelUtils.create_bet(u2, g2, 2, 2)
        gb6 = TestModelUtils.create_bet(u2, g4, 1, 1)
        gb7 = TestModelUtils.create_bet(u2, g1, 0, 3)
        gb8 = TestModelUtils.create_bet(u2, g3, 4, 2)
        gb9 = TestModelUtils.create_bet(u2, g5, 0, 0)

        # reply only those bets that are owned by the user or deadline has passed
        self.create_test_user(u1.username)
        bets = self.client.get(self.GAMEBETS_BASEURL).data
        self.assertEqual(7, len(bets))
        self.assertEqual([gb.id for gb in [gb1, gb2, gb3, gb4, gb5, gb6, gb7]], [gb['id'] for gb in bets])

        # test filtering by user_id
        bets = self.client.get('%s?user_id=%i' % (self.GAMEBETS_BASEURL, u1.pk)).data
        self.assertEqual(4, len(bets))
        self.assertEqual([gb.id for gb in [gb1, gb2, gb3, gb4]], [gb['id'] for gb in bets])

        # test filtering by user_id - foreign user
        bets = self.client.get('%s?user_id=%i' % (self.GAMEBETS_BASEURL, u2.pk)).data
        self.assertEqual(3, len(bets))
        self.assertEqual([gb.id for gb in [gb5, gb6, gb7]], [gb['id'] for gb in bets])

        self.create_test_user(u2.username)
        bets = self.client.get(self.GAMEBETS_BASEURL).data
        self.assertEqual(7, len(bets))
        self.assertEqual([gb.id for gb in [gb1, gb2, gb5, gb6, gb7, gb8, gb9]], [gb['id'] for gb in bets])

    def test_gamebet_public_read(self):
        self.create_test_user(auth=False)
        response = self.get_test_gamebet_api()
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_gamebet_create_deadlines(self):
        """
            A user must not be able to create a bet for a game where the deadline has passed already
            The attempt will raise a 400 (Bad Request), because POSTing itself is allowed, but validation will fail
        """
        u1 = TestModelUtils.create_user()

        g1 = TestModelUtils.create_game()    # kicks off NOW
        g2 = TestModelUtils.create_game(kickoff=TestModelUtils.create_datetime_from_now(timedelta(hours=2)))

        self.create_test_user(u1.username)
        create_disallowed = self.client.post(self.GAMEBETS_BASEURL, {'homegoals': 3, 'awaygoals': 2, 'game': g1.pk},
                                             format='json')
        self.assertEqual(status.HTTP_400_BAD_REQUEST, create_disallowed.status_code)

        create_allowed = self.client.post(self.GAMEBETS_BASEURL, {'homegoals': 0, 'awaygoals': 0, 'game': g2.pk},
                                          format='json')
        self.assertEqual(status.HTTP_201_CREATED, create_allowed.status_code)

    def test_gamebet_create_other(self):
        """
            A user may not create a bet for a user other than himself. He can try to, but the user will always be
            automatically set to himself, because it is not writable and set to the request user by default
        """
        u1, u2 = TestModelUtils.create_user(), TestModelUtils.create_user()

        g1 = TestModelUtils.create_game(kickoff=TestModelUtils.create_datetime_from_now(timedelta(hours=2)))  # bets open

        self.create_test_user(u2.username)
        create_unsuccessful = self.client.post(self.GAMEBETS_BASEURL, {'homegoals': 0, 'awaygoals': 2, 'game': g1.pk,
                                                                       'user': u1.pk}, format='json')
        self.assertEqual(status.HTTP_201_CREATED, create_unsuccessful.status_code)
        self.assertEqual(u2.pk, GameBet.objects.get(game__pk=g1.pk).user.id)        # user has been overwritten by self!

        GameBet.objects.all().delete()

        create_successful = self.client.post(self.GAMEBETS_BASEURL, {'homegoals': 3, 'awaygoals': 2, 'game': g1.pk,
                                                                     'user': u2.pk}, format='json')
        self.assertEqual(status.HTTP_201_CREATED, create_successful.status_code)
        self.assertEqual(u2.pk, GameBet.objects.get(game__pk=g1.pk).user.id)


    def test_gamebet_update_deadlines(self):
        """
            An authenticated user must not be allowed to update his bet for a game where the deadline has passed already
        """
        u1 = TestModelUtils.create_user()

        g1 = TestModelUtils.create_game()    # kicks off NOW
        g2 = TestModelUtils.create_game(kickoff=TestModelUtils.create_datetime_from_now(timedelta(hours=2)))

        gb1 = TestModelUtils.create_bet(u1, g1, 2, 1)
        gb2 = TestModelUtils.create_bet(u1, g2)

        self.create_test_user(u1.username)
        update_disallowed = self.client.put("%s%i/" % (self.GAMEBETS_BASEURL, gb1.pk),
                                            {'homegoals': 3, 'awaygoals': 2, 'game': g1.pk}, format='json')
        self.assertEqual(status.HTTP_400_BAD_REQUEST, update_disallowed.status_code)

        update_allowed = self.client.put("%s%i/" % (self.GAMEBETS_BASEURL, gb2.pk),
                                         {'homegoals': 0, 'awaygoals': 0, 'game': g2.pk}, format='json')
        self.assertEqual(status.HTTP_200_OK, update_allowed.status_code)

    def test_gamebet_update_other(self):
        """
            A user must not be allowed to update a bet of a different user.
            The attempt will receive a 404 because not owned bets are excluded from the viewset using a filter.
        """
        u1, u2 = TestModelUtils.create_user(), TestModelUtils.create_user()

        g1 = TestModelUtils.create_game(kickoff=TestModelUtils.create_datetime_from_now(timedelta(hours=2)))  # bets open
        gb1 = TestModelUtils.create_bet(u1, g1, 2, 1)

        self.create_test_user(u2.username)
        update_disallowed = self.client.put("%s%i/" % (self.GAMEBETS_BASEURL, gb1.pk),
                                            {'homegoals': 3, 'awaygoals': 2, 'game': g1.pk}, format='json')
        self.assertEqual(status.HTTP_404_NOT_FOUND, update_disallowed.status_code)

    def test_gamebet_delete_other(self):
        """
            A user may only delete his own bet.
            A DELETE request on another user's bet actually returns a 404 (Not Found), because it's filtered out by the viewset.
        """
        u1, u2 = TestModelUtils.create_user(), TestModelUtils.create_user()

        g1 = TestModelUtils.create_game(kickoff=TestModelUtils.create_datetime_from_now(timedelta(hours=2)))  # bets open
        gb1 = TestModelUtils.create_bet(u1, g1, 2, 1)

        self.create_test_user(u2.username)
        delete_disallowed = self.client.delete("%s%i/" % (self.GAMEBETS_BASEURL, gb1.pk))
        self.assertEqual(status.HTTP_404_NOT_FOUND, delete_disallowed.status_code)

        self.create_test_user(u1.username)
        delete_disallowed = self.client.delete("%s%i/" % (self.GAMEBETS_BASEURL, gb1.pk))
        self.assertEqual(status.HTTP_204_NO_CONTENT, delete_disallowed.status_code)

    def test_gamebet_update(self):
        self.create_test_user()
        response = self.update_test_gamebet_api()
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_gamebet_delete_admin(self):
        self.create_test_user(admin=True)
        response = self.delete_test_gamebet_api()
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(GameBet.objects.count(), 0)

    def test_gamebet_delete(self):
        self.create_test_user()
        response = self.delete_test_gamebet_api()
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_gamebet_delete_public(self):
        self.create_test_user(auth=False)
        response = self.delete_test_gamebet_api()
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    @staticmethod
    def create_test_gamebet(user):
        test_game = GameApiTests.create_test_game()
        test_gamebet = GameBet(homegoals=4, awaygoals=2, game=test_game, user=user)
        test_gamebet.save()
        return test_gamebet

    def get_test_gamebet_api(self):
        test_gamebet = self.create_test_gamebet(self.test_user)
        return self.client.get('%s%i/' % (self.GAMEBETS_BASEURL, test_gamebet.pk))

    def create_test_gamebet_api(self):
        test_game = GameApiTests.create_test_game()
        return self.client.post(self.GAMEBETS_BASEURL, {'homegoals': 5, 'awaygoals': 1, 'game': test_game.pk},
                                format='json')

    def update_test_gamebet_api(self):
        test_gamebet = self.create_test_gamebet(self.test_user)
        test_game = GameApiTests.create_test_game()
        return self.client.put("%s%i/" % (self.GAMEBETS_BASEURL, test_gamebet.pk),
                               {'homegoals': 3, 'awaygoals': 2, 'game': test_game.pk}, format='json')

    def delete_test_gamebet_api(self):
        test_gamebet = self.create_test_gamebet(self.test_user)
        return self.client.delete("%s%i/" % (self.GAMEBETS_BASEURL, test_gamebet.pk))