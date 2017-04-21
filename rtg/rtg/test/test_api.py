import json
from datetime import timedelta
from django.contrib.auth.models import User
from django.db import transaction

from rest_framework import status
from rest_framework.test import APITestCase
from rtg.models import Profile, TournamentGroup, TournamentRound, Team, Venue, Game, ExtraBet, Extra, ExtraChoice, \
    GameBet


# TODO test invalid requests (at least for bets)
# TODO create some more advanced tests
from rtg.test.utils import TestModelUtils


class RtgApiTestCase(APITestCase):

    # TODO DRF's reverse function not working here
    GROUPS_BASEURL = '/rtg/tournamentgroups/'
    ROUNDS_BASEURL = '/rtg/tournamentrounds/'
    TEAMS_BASEURL = '/rtg/teams/'
    VENUES_BASEURL = '/rtg/venues/'
    GAMES_BASEURL = '/rtg/games/'
    GAMEBETS_BASEURL = '/rtg/gamebets/'
    EXTRAS_BASEURL = '/rtg/extras/'
    EXTRACHOICES_BASEURL = '/rtg/extrachoices/'
    EXTRABETS_BASEURL = '/rtg/extrabets/'
    USERS_BASEURL = '/rtg/users/'
    PROFILES_BASEURL = '/rtg/profiles/'

    def create_test_user(self, name='test_user', auth=True, admin=False):
        try:
            user = User.objects.get(username=name)
            user.is_staff = admin
        except User.DoesNotExist:
            user = User(username=name, is_staff=admin)

        user.save()

        if auth:
            self.set_api_client(user)
        self.test_user = user
        return user

    def set_api_client(self, user):
        self.client.force_authenticate(user=user)


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


class VenueApiTests(RtgApiTestCase):

    def tearDown(self):
        self.delete_test_venue()

    def test_venue_create(self):
        self.create_test_user(admin=True)
        response = self.create_test_venue_api()
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Venue.objects.count(), 1)
        self.assertIsNotNone(Venue.objects.get(name='RTG National Stadium'))

    def test_venue_create_unauth(self):
        self.create_test_user()
        response = self.create_test_venue_api()
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_venue_read(self):
        self.create_test_user()
        response = self.get_test_venue_api()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Venue.objects.count(), 1)
        self.assertIsNotNone(Venue.objects.get(name='RTG National Stadium'))

    def test_venue_public_read(self):
        self.create_test_user(auth=False)
        response = self.get_test_venue_api()
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_venue_update(self):
        self.create_test_user(admin=True)
        response = self.update_test_venue_api()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Venue.objects.count(), 1)
        self.assertIsNotNone(Venue.objects.get(name='RTG Regional Field'))
        self.assertRaises(Venue.DoesNotExist, Venue.objects.get, name='RTG National Stadium')

    def test_venue_update_unauth(self):
        self.create_test_user()
        response = self.update_test_venue_api()
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_venue_delete(self):
        self.create_test_user(admin=True)
        response = self.delete_test_venue_api()
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Venue.objects.count(), 0)

    def test_venue_delete_unauth(self):
        self.create_test_user()
        response = self.delete_test_venue_api()
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_venue_delete_public(self):
        self.create_test_user(auth=False)
        response = self.delete_test_venue_api()
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    @staticmethod
    def create_test_venue():
        try:
            test_venue = Venue.objects.get(name='RTG National Stadium')
        except Venue.DoesNotExist:
            test_venue = Venue(name='RTG National Stadium', city='Glamour City', capacity=90000)
            test_venue.save()
        return test_venue

    @staticmethod
    def delete_test_venue():
        try:
            test_venue = Venue.objects.get(name='RTG National Stadium')
            test_venue.delete()
        except Venue.DoesNotExist:
            pass

    def get_test_venue_api(self):
        self.create_test_venue()
        venue_pk = Venue.objects.get(name='RTG National Stadium').pk
        return self.client.get('%s%i/' % (self.VENUES_BASEURL, venue_pk))

    def create_test_venue_api(self):
        return self.client.post(self.VENUES_BASEURL, {'name': 'RTG National Stadium', 'city': 'Glamour City',
                                                      'capacity': 90000}, format='json')

    def update_test_venue_api(self):
        self.create_test_venue()
        venue_pk = Venue.objects.get(name='RTG National Stadium').pk
        return self.client.put("%s%i/" % (self.VENUES_BASEURL, venue_pk),
                               {'name': 'RTG Regional Field', 'city': 'Simplicity Valley',
                                'capacity': 1909}, format='json')

    def delete_test_venue_api(self):
        self.create_test_venue()
        venue_pk = Venue.objects.get(name='RTG National Stadium').pk
        return self.client.delete("%s%i/" % (self.VENUES_BASEURL, venue_pk))


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

        gb1 = TestModelUtils.create_gamebet(u1, g1, 2, 1)
        gb2 = TestModelUtils.create_gamebet(u1, g2, 0, 1)
        gb3 = TestModelUtils.create_gamebet(u1, g3, 1, 3)
        gb4 = TestModelUtils.create_gamebet(u1, g5, 1, 3)

        gb5 = TestModelUtils.create_gamebet(u2, g2, 2, 2)
        gb6 = TestModelUtils.create_gamebet(u2, g4, 1, 1)
        gb7 = TestModelUtils.create_gamebet(u2, g1, 0, 3)
        gb8 = TestModelUtils.create_gamebet(u2, g3, 4, 2)
        gb9 = TestModelUtils.create_gamebet(u2, g5, 0, 0)

        # reply only those bets that are owned by the user or deadline has passed
        self.create_test_user(u1.username)
        response = list(self.client.get(self.GAMEBETS_BASEURL))[0]
        bets = json.loads(response)
        self.assertEqual(7, len(bets))
        self.assertEqual([gb.id for gb in [gb1, gb2, gb3, gb4, gb5, gb6, gb7]], [gb['id'] for gb in bets])

        # test filtering by user_id
        response = list(self.client.get('%s?user_id=%i' % (self.GAMEBETS_BASEURL, u1.pk)))[0]
        bets = json.loads(response)
        self.assertEqual(4, len(bets))
        self.assertEqual([gb.id for gb in [gb1, gb2, gb3, gb4]], [gb['id'] for gb in bets])

        # test filtering by user_id - foreign user
        response = list(self.client.get('%s?user_id=%i' % (self.GAMEBETS_BASEURL, u2.pk)))[0]
        bets = json.loads(response)
        self.assertEqual(3, len(bets))
        self.assertEqual([gb.id for gb in [gb5, gb6, gb7]], [gb['id'] for gb in bets])

        self.create_test_user(u2.username)
        response = list(self.client.get(self.GAMEBETS_BASEURL))[0]
        bets = json.loads(response)
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

        gb1 = TestModelUtils.create_gamebet(u1, g1, 2, 1)
        gb2 = TestModelUtils.create_gamebet(u1, g2)

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
        gb1 = TestModelUtils.create_gamebet(u1, g1, 2, 1)

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
        gb1 = TestModelUtils.create_gamebet(u1, g1, 2, 1)

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


class ExtraApiTests(RtgApiTestCase):

    def tearDown(self):
        pass

    def test_extra_create(self):
        self.create_test_user(admin=True)
        response = self.create_test_extra_api()
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Extra.objects.count(), 1)
        self.assertIsNotNone(Extra.objects.get(name='Extrawurst'))

    def test_extra_create_unauth(self):
        self.create_test_user()
        response = self.create_test_extra_api()
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_extra_read(self):
        self.create_test_user()
        response = self.get_test_extra_api()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Extra.objects.count(), 1)
        self.assertIsNotNone(Extra.objects.get(name='Extrawurst'))

    def test_extra_public_read(self):
        self.create_test_user(auth=False)
        response = self.get_test_extra_api()
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_extra_update(self):
        self.create_test_user(admin=True)
        response = self.update_test_extra_api()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Extra.objects.count(), 1)

        stored_extra = list(Extra.objects.all()[:1])[0]
        self.assertIsNotNone(stored_extra)
        self.assertEquals(stored_extra.name, 'Sonderbehandlung')
        self.assertEquals(stored_extra.points, 101)
        self.assertRaises(Extra.DoesNotExist, Extra.objects.get, name='Extrawurst')

    def test_extra_update_unauth(self):
        self.create_test_user()
        response = self.update_test_extra_api()
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_extra_delete(self):
        self.create_test_user(admin=True)
        response = self.delete_test_extra_api()
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Extra.objects.count(), 0)

    def test_extra_delete_unauth(self):
        self.create_test_user()
        response = self.delete_test_extra_api()
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_extra_delete_public(self):
        self.create_test_user(auth=False)
        response = self.delete_test_extra_api()
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    @staticmethod
    def create_test_extra():
        try:
            test_extra = Extra.objects.get(name='Extrawurst')
        except Extra.DoesNotExist:
            test_extra = Extra(name='Extrawurst', points=100, deadline='2016-06-06 18:00:00+0000', result='Salami')
            test_extra.save()
        return test_extra

    def get_test_extra_api(self):
        test_extra = self.create_test_extra()
        return self.client.get('%s%i/' % (self.EXTRAS_BASEURL, test_extra.pk))

    def create_test_extra_api(self):
        return self.client.post(self.EXTRAS_BASEURL,
                                {'name': 'Extrawurst', 'points': 100, 'deadline': '2016-06-06 18:00:00+0000',
                                 'result': 'Salami'}, format='json')

    def update_test_extra_api(self):
        test_extra = self.create_test_extra()
        return self.client.put("%s%i/" % (self.EXTRAS_BASEURL, test_extra.pk),
                               {'name': 'Sonderbehandlung', 'points': 101, 'deadline': '2016-08-08 20:00:00+0000',
                                'result': 'Schinkenwurst'}, format='json')

    def delete_test_extra_api(self):
        test_extra = self.create_test_extra()
        return self.client.delete("%s%i/" % (self.EXTRAS_BASEURL, test_extra.pk))


class ExtraChoiceApiTests(RtgApiTestCase):

    def tearDown(self):
        pass

    def test_extrachoice_create(self):
        self.create_test_user(admin=True)
        response = self.create_test_extrachoice_api()
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(ExtraChoice.objects.count(), 1)
        self.assertIsNotNone(ExtraChoice.objects.get(name='Salami'))

    def test_extrachoice_create_unauth(self):
        self.create_test_user()
        response = self.create_test_extrachoice_api()
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_extrachoice_read(self):
        self.create_test_user()
        response = self.get_test_extrachoice_api()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(ExtraChoice.objects.count(), 1)
        self.assertIsNotNone(ExtraChoice.objects.get(name='Salami'))

    def test_extrachoice_public_read(self):
        self.create_test_user(auth=False)
        response = self.get_test_extrachoice_api()
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_extrachoice_update(self):
        self.create_test_user(admin=True)
        response = self.update_test_extrachoice_api()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(ExtraChoice.objects.count(), 1)

        stored_extrachoice = list(ExtraChoice.objects.all()[:1])[0]
        self.assertIsNotNone(stored_extrachoice)
        self.assertEquals(stored_extrachoice.name, 'Schinkenwurst')
        self.assertEquals(stored_extrachoice.sort_index, '456')
        self.assertRaises(ExtraChoice.DoesNotExist, ExtraChoice.objects.get, name='Salami')

    def test_extrachoice_update_unauth(self):
        self.create_test_user()
        response = self.update_test_extrachoice_api()
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_extrachoice_delete(self):
        self.create_test_user(admin=True)
        response = self.delete_test_extrachoice_api()
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(ExtraChoice.objects.count(), 0)

    def test_extrachoice_delete_unauth(self):
        self.create_test_user()
        response = self.delete_test_extrachoice_api()
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_extrachoice_delete_public(self):
        self.create_test_user(auth=False)
        response = self.delete_test_extrachoice_api()
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    @staticmethod
    def create_test_extrachoice():
        try:
            test_extrachoice = ExtraChoice.objects.get(name='Salami')
        except ExtraChoice.DoesNotExist:
            test_extra = ExtraApiTests.create_test_extra()
            test_extrachoice = ExtraChoice(name='Salami', extra=test_extra, sort_index='123')
            test_extrachoice.save()
        return test_extrachoice

    def get_test_extrachoice_api(self):
        test_extrachoice = self.create_test_extrachoice()
        return self.client.get('%s%i/' % (self.EXTRACHOICES_BASEURL, test_extrachoice.pk))

    def create_test_extrachoice_api(self):
        test_extra = ExtraApiTests.create_test_extra()
        return self.client.post(self.EXTRACHOICES_BASEURL,
                                {'name': 'Salami', 'extra': test_extra.pk, 'sort_index': '123'}, format='json')

    def update_test_extrachoice_api(self):
        test_extra = ExtraApiTests.create_test_extra()
        test_extrachoice = self.create_test_extrachoice()
        return self.client.put("%s%i/" % (self.EXTRACHOICES_BASEURL, test_extrachoice.pk),
                               {'name': 'Schinkenwurst', 'extra': test_extra.pk, 'sort_index': '456'}, format='json')

    def delete_test_extrachoice_api(self):
        test_extrachoice = self.create_test_extrachoice()
        return self.client.delete("%s%i/" % (self.EXTRACHOICES_BASEURL, test_extrachoice.pk))


class ExtraBetApiTests(RtgApiTestCase):

    def tearDown(self):
        ExtraBet.objects.all().delete()

    def test_extrabet_create_admin(self):
        self.create_test_user(admin=True)
        response = self.create_test_extrabet_api()
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(ExtraBet.objects.count(), 1)
        self.assertIsNotNone(ExtraBet.objects.get(result_bet='Lyoner'))

    def test_extrabet_create(self):
        u1 = TestModelUtils.create_user()
        self.create_test_user(u1.username)
        response = self.create_test_extrabet_api()
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(ExtraBet.objects.count(), 1)
        self.assertIsNotNone(ExtraBet.objects.get(result_bet='Lyoner'))
        self.assertEqual(u1.pk, ExtraBet.objects.get(result_bet='Lyoner').user.id)

    def test_extrabet_create_public(self):
        self.create_test_user(auth=False)
        response = self.create_test_extrabet_api()
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_extrabet_read(self):
        # TODO apply restrictions when trying to read bets created by other users
        self.create_test_user()
        response = self.get_test_extrabet_api()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(ExtraBet.objects.count(), 1)
        self.assertIsNotNone(ExtraBet.objects.get(result_bet='Lyoner'))

    def test_extrabet_read_allowed(self):
        u1, u2 = TestModelUtils.create_user(), TestModelUtils.create_user()

        e1 = TestModelUtils.create_extra(deadline=TestModelUtils.create_datetime_from_now(timedelta(days=-2)))
        e2 = TestModelUtils.create_extra(deadline=TestModelUtils.create_datetime_from_now(timedelta(hours=5)))
        e3 = TestModelUtils.create_extra(deadline=TestModelUtils.create_datetime_from_now(timedelta(hours=-1)))
        e4 = TestModelUtils.create_extra(deadline=TestModelUtils.create_datetime_from_now(timedelta(days=12)))

        eb1 = TestModelUtils.create_extrabet('foo', e1, u1)
        eb2 = TestModelUtils.create_extrabet('bar', e2, u1)
        eb3 = TestModelUtils.create_extrabet('baz', e3, u1)

        eb5 = TestModelUtils.create_extrabet('bee', e4, u2)
        eb6 = TestModelUtils.create_extrabet('bling', e2, u2)
        eb7 = TestModelUtils.create_extrabet('blang', e1, u2)
        eb8 = TestModelUtils.create_extrabet('blong', e3, u2)

        # reply only those bets that are owned by the user or deadline has passed
        self.create_test_user(u1.username)
        response = list(self.client.get(self.EXTRABETS_BASEURL))[0]
        bets = json.loads(response)
        self.assertEqual(5, len(bets))
        self.assertEqual([eb.id for eb in [eb1, eb2, eb3, eb7, eb8]], [eb['id'] for eb in bets])

        self.create_test_user(u2.username)
        response = list(self.client.get(self.EXTRABETS_BASEURL))[0]
        bets = json.loads(response)
        self.assertEqual(6, len(bets))
        self.assertEqual([eb.id for eb in [eb1, eb3, eb5, eb6, eb7, eb8]], [eb['id'] for eb in bets])

    def test_extrabet_public_read(self):
        self.create_test_user(auth=False)
        response = self.get_test_extrabet_api()
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_extrabet_create_deadlines(self):
        """
            cf. GameBet test
        """
        u1 = TestModelUtils.create_user()

        e1 = TestModelUtils.create_extra()    # deadline is NOW
        e2 = TestModelUtils.create_extra(deadline=TestModelUtils.create_datetime_from_now(timedelta(hours=2)))

        self.create_test_user(u1.username)
        create_disallowed = self.client.post(self.EXTRABETS_BASEURL, {'result_bet': 'zilch', 'extra': e1.pk},
                                             format='json')
        self.assertEqual(status.HTTP_400_BAD_REQUEST, create_disallowed.status_code)

        create_allowed = self.client.post(self.EXTRABETS_BASEURL, {'result_bet': 'nuts', 'extra': e2.pk},
                                          format='json')
        self.assertEqual(status.HTTP_201_CREATED, create_allowed.status_code)

    def test_extrabet_create_other(self):
        """
            cf. GameBet test
        """
        u1, u2 = TestModelUtils.create_user(), TestModelUtils.create_user()

        e1 = TestModelUtils.create_extra(deadline=TestModelUtils.create_datetime_from_now(timedelta(hours=2)))  # bets open

        self.create_test_user(u2.username)
        create_unsuccessful = self.client.post(self.EXTRABETS_BASEURL, {'result_bet': 'blubb', 'extra': e1.pk,
                                                                        'user': u1.pk}, format='json')
        self.assertEqual(status.HTTP_201_CREATED, create_unsuccessful.status_code)
        self.assertEqual(u2.pk, ExtraBet.objects.get(extra__pk=e1.pk).user.id)        # user has been overwritten by self!

        ExtraBet.objects.all().delete()

        create_successful = self.client.post(self.EXTRABETS_BASEURL, {'result_bet': 'flapp', 'extra': e1.pk,
                                                                      'user': u2.pk}, format='json')
        self.assertEqual(status.HTTP_201_CREATED, create_successful.status_code)
        self.assertEqual(u2.pk, ExtraBet.objects.get(extra__pk=e1.pk).user.id)

    def test_extrabet_update_deadlines(self):
        """
            cf. GameBet test
        """
        u1 = TestModelUtils.create_user()

        e1 = TestModelUtils.create_extra()    # deadline is NOW
        e2 = TestModelUtils.create_extra(deadline=TestModelUtils.create_datetime_from_now(timedelta(hours=2)))

        eb1 = TestModelUtils.create_extrabet('fubu', e1, u1)
        eb2 = TestModelUtils.create_extrabet('faba', e2, u1)

        self.create_test_user(u1.username)
        update_disallowed = self.client.put("%s%i/" % (self.EXTRABETS_BASEURL, eb1.pk),
                                            {'result_bet': 'fibi', 'extra': e1.pk}, format='json')
        self.assertEqual(status.HTTP_400_BAD_REQUEST, update_disallowed.status_code)

        update_allowed = self.client.put("%s%i/" % (self.EXTRABETS_BASEURL, eb2.pk),
                                         {'result_bet': 'febe', 'extra': e2.pk}, format='json')
        self.assertEqual(status.HTTP_200_OK, update_allowed.status_code)

    def test_extrabet_update_other(self):
        """
            cf. GameBet test
        """
        u1, u2 = TestModelUtils.create_user(), TestModelUtils.create_user()

        e1 = TestModelUtils.create_extra(deadline=TestModelUtils.create_datetime_from_now(timedelta(hours=2)))  # bets open
        eb1 = TestModelUtils.create_extrabet('zonk', e1, u1)

        self.create_test_user(u2.username)
        update_disallowed = self.client.put("%s%i/" % (self.EXTRABETS_BASEURL, eb1.pk),
                                            {'result_bet': 'zink', 'extra': e1.pk}, format='json')
        self.assertEqual(status.HTTP_404_NOT_FOUND, update_disallowed.status_code)

    def test_extrabet_delete_other(self):
        """
            cf. GameBet test
        """
        u1, u2 = TestModelUtils.create_user(), TestModelUtils.create_user()

        e1 = TestModelUtils.create_extra(deadline=TestModelUtils.create_datetime_from_now(timedelta(hours=2)))  # bets open
        eb1 = TestModelUtils.create_extrabet('bummer', e1, u1)

        self.create_test_user(u2.username)
        delete_disallowed = self.client.delete("%s%i/" % (self.EXTRABETS_BASEURL, eb1.pk))
        self.assertEqual(status.HTTP_404_NOT_FOUND, delete_disallowed.status_code)

        self.create_test_user(u1.username)
        delete_disallowed = self.client.delete("%s%i/" % (self.EXTRABETS_BASEURL, eb1.pk))
        self.assertEqual(status.HTTP_204_NO_CONTENT, delete_disallowed.status_code)

    def test_extrabet_update(self):
        self.create_test_user()
        response = self.update_test_extrabet_api()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(ExtraBet.objects.count(), 1)

        stored_extrabet = list(ExtraBet.objects.all()[:1])[0]
        self.assertIsNotNone(stored_extrabet)
        self.assertEquals(stored_extrabet.result_bet, 'Paprikasalami')
        self.assertRaises(ExtraBet.DoesNotExist, ExtraBet.objects.get, result_bet='Lyoner')

    def test_extrabet_delete_admin(self):
        self.create_test_user(admin=True)
        response = self.delete_test_extrabet_api()
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(ExtraBet.objects.count(), 0)

    def test_extrabet_delete(self):
        self.create_test_user()
        response = self.delete_test_extrabet_api()
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_extrabet_delete_public(self):
        self.create_test_user(auth=False)
        response = self.delete_test_extrabet_api()
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    @staticmethod
    def create_test_extrabet(user):
        test_extra = ExtraApiTests.create_test_extra()
        test_extrabet = ExtraBet(result_bet='Lyoner', extra=test_extra, user=user)
        test_extrabet.save()
        return test_extrabet

    def get_test_extrabet_api(self):
        test_extrabet = self.create_test_extrabet(self.test_user)
        return self.client.get('%s%i/' % (self.EXTRABETS_BASEURL, test_extrabet.pk))

    def create_test_extrabet_api(self):
        test_extra = ExtraApiTests.create_test_extra()
        return self.client.post(self.EXTRABETS_BASEURL, {'result_bet': 'Lyoner', 'extra': test_extra.pk}, format='json')

    def update_test_extrabet_api(self):
        test_extrabet = self.create_test_extrabet(self.test_user)
        test_extra = ExtraApiTests.create_test_extra()
        return self.client.put("%s%i/" % (self.EXTRABETS_BASEURL, test_extrabet.pk),
                               {'result_bet': 'Paprikasalami', 'extra': test_extra.pk}, format='json')

    def delete_test_extrabet_api(self):
        test_extrabet = self.create_test_extrabet(self.test_user)
        return self.client.delete("%s%i/" % (self.EXTRABETS_BASEURL, test_extrabet.pk))


class UserApiTests(RtgApiTestCase):
    """
        Users are read_only via the API, except for updates of the own user
    """

    def test_user_create(self):
        self.create_test_user(admin=True)
        response = self.create_test_user_api()
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_user_create_unauth(self):
        self.create_test_user()
        response = self.create_test_user_api()
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_user_read(self):
        u1, u2 = TestModelUtils.create_user(), TestModelUtils.create_user()

        self.set_api_client(u1)

        response = self.client.get('%s%i/' % (self.USERS_BASEURL, u1.pk))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['username'], u1.username)
        self.assertIsNotNone(response.data['first_name'])
        self.assertIsNotNone(response.data['last_name'])
        self.assertIsNotNone(response.data['email'])

        # other users may be read, but only their username
        response = self.client.get('%s%i/' % (self.USERS_BASEURL, u2.pk))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['username'], u2.username)
        self.assertIsNone(response.data['first_name'])
        self.assertIsNone(response.data['last_name'])
        self.assertIsNone(response.data['email'])

    def test_user_read_list(self):
        u1, u2, u3 = TestModelUtils.create_user(), TestModelUtils.create_user(), TestModelUtils.create_user()

        self.set_api_client(u1)

        response = self.client.get(self.USERS_BASEURL)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        users = json.loads(list(response)[0])
        self.assertEqual(3, len(users))

    def test_user_read_admin(self):
        u1, u2 = TestModelUtils.create_user(), TestModelUtils.create_user()

        self.create_test_user(name=u1.username, admin=True)

        # admins may read all user details, even of different users
        response = self.client.get('%s%i/' % (self.USERS_BASEURL, u2.pk))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['username'], u2.username)
        self.assertEqual(response.data['first_name'], u2.first_name)
        self.assertEqual(response.data['last_name'], u2.last_name)
        self.assertEqual(response.data['email'], u2.email)

    def test_user_public_read(self):
        public_user = self.create_test_user(auth=False)
        response = self.client.get('%s%i/' % (self.USERS_BASEURL, public_user.pk))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_user_update_other_user_as_admin(self):
        u1 = self.create_test_user('u1')
        self.create_test_user('admin_user', admin=True)

        response = self.client.put("%s%i/" % (self.USERS_BASEURL, u1.pk), {'username': 'newuser'}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        updated_user = User.objects.get(username='newuser')
        self.assertIsNotNone(updated_user)
        self.assertEqual(updated_user.username, 'newuser')
        self.assertRaises(User.DoesNotExist, User.objects.get, username='u1')

    def test_user_update_other_user_forbidden(self):
        u1 = self.create_test_user('u1')
        self.create_test_user('u2')

        response = self.client.put("%s%i/" % (self.USERS_BASEURL, u1.pk), {'username': 'newuser'}, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_user_update_self(self):
        u1 = self.create_test_user('u1')
        response = self.client.put("%s%i/" % (self.USERS_BASEURL, u1.pk), {'username': 'newuser'}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        updated_user = User.objects.get(username='newuser')
        self.assertIsNotNone(updated_user)
        self.assertEqual(updated_user.username, 'newuser')
        self.assertRaises(User.DoesNotExist, User.objects.get, username='u1')

    def test_user_update_public(self):
        u1 = self.create_test_user('u1', auth=False)
        response = self.client.put("%s%i/" % (self.USERS_BASEURL, u1.pk), {'username': 'newuser'}, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_user_delete_admin(self):
        self.create_test_user(admin=True)
        response = self.delete_test_user_api()
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_user_delete_authuser(self):
        self.create_test_user()
        response = self.delete_test_user_api()
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def create_test_user_api(self):
        return self.client.post(self.USERS_BASEURL, {'username': 'test_user'}, format='json')

    def delete_test_user_api(self):
        test_user = self.create_test_user()
        return self.client.delete("%s%i/" % (self.USERS_BASEURL, test_user.pk))


# class ProfileApiTests(RtgApiTestCase):
#
#     def setUp(self):
#         self.create_test_user(admin=True)
#
#     def test_profile_being_created(self):
#         response = self.client.post(self.USERS_BASEURL, {'username': 'jacklondon'}, format='json')
#         self.assertEqual(response.status_code, status.HTTP_201_CREATED)
#
#         user_pk = User.objects.get(username='jacklondon').pk
#         response = self.client.get('%s%i/' % (self.PROFILES_BASEURL, user_pk))
#         self.assertEqual(response.status_code, status.HTTP_200_OK)
#
#         self.assertIsNotNone(Profile.objects.get(user__pk=user_pk))
#         self.assertEqual('jacklondon', response.data['user']['username'])