# -*- coding: utf-8 -*-
from datetime import timedelta

from django.contrib.auth.models import User
from rest_framework import status

from main.models import Profile
from main.test.api.abstract_rtg_api_test import RtgApiTestCase
from main.test.utils import TestModelUtils


class PublicUserApiTests(RtgApiTestCase):
    """
        Public users are read_only for all authenticated users, they only contain fields which everyone may see
    """

    def setUp(self):
        User.objects.all().delete()
        Profile.objects.all().delete()

    def test_user_read_only_active(self):
        """ Only users which have logged in this year should be returned """
        u1, u2, u3 = TestModelUtils.create_user(), TestModelUtils.create_user(), TestModelUtils.create_user()

        u1.last_login = TestModelUtils.create_datetime_from_now()
        u2.last_login = TestModelUtils.create_datetime_from_now(timedelta(days=365))
        u1.save()
        u2.save()

        self.set_api_client(u1)

        response = self.client.get('%s' % self.PUBLIC_USERS_BASEURL)
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(1, len(response.data))
        self.assertEqual(u1.username, response.data[0]['username'])
