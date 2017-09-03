# -*- coding: utf-8 -*-
from django.contrib.auth.models import User
from rest_framework.test import APITestCase
# TODO test invalid requests (at least for bets)
# TODO create some more advanced tests


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