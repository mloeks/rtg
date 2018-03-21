# -*- coding: utf-8 -*-

from rest_framework import status, response

from main.test.api.abstract_rtg_api_test import RtgApiTestCase
from main.test.utils import TestModelUtils
from main.models import Profile


class ProfileApiTests(RtgApiTestCase):
    def setUp(self):
        Profile.objects.all().delete()

    def test_profile_create_not_possible(self):
        """ Profile's may never be created directly via the API """
        u1 = TestModelUtils.create_user()
        self.set_api_client(u1)

        response = self.client.post(self.PROFILES_BASEURL,
                         {'email2': 'mail@mail2.de', 'location': 'Kölle', 'about': 'It\'s me', 'avatar': None,
                          'avatar_url': None, 'daily_emails': True, 'reminder_emails': True}, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_profile_put(self):
        u1 = TestModelUtils.create_user() # this will also create a new profile...
        self.set_api_client(u1)

        response = self.client.put("%s%s/" % (self.PROFILES_BASEURL, u1.pk),
                                    {'pk': u1.pk, 'email2': 'mail@mail2.de', 'location': 'Kölle', 'about': 'It\'s me',
                                     'avatar': None, 'avatar_url': None, 'daily_emails': False, 'reminder_emails': True},
                                   format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        updated_profile = Profile.objects.get(pk=u1.pk)
        self.assertEqual('mail@mail2.de', updated_profile.email2)
        self.assertEqual('Kölle', updated_profile.location)
        self.assertEqual('It\'s me', updated_profile.about)
        self.assertFalse(updated_profile.daily_emails)
