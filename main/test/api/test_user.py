# -*- coding: utf-8 -*-
import json

from django.contrib.auth.models import User
from rest_framework import status

from main.test.api.abstract_rtg_api_test import RtgApiTestCase
from main.test.utils import TestModelUtils
from main.models import Profile


class UserApiTests(RtgApiTestCase):
    """
        Users are read_only via the API, except for updates of the own user
    """

    def setUp(self):
        User.objects.all().delete()
        Profile.objects.all().delete()

    def test_user_create(self):
        self.create_test_user(admin=True)
        response = self.create_test_user_api()
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_user_create_non_admin(self):
        self.create_test_user()
        response = self.create_test_user_api()
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_user_create_unauth(self):
        self.create_test_user(auth=False)
        response = self.create_test_user_api()
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_user_read(self):
        u1, u2 = TestModelUtils.create_user(), TestModelUtils.create_user()

        self.set_api_client(u1)

        response = self.client.get('%s%i/' % (self.USERS_BASEURL, u1.pk))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['username'], u1.username)
        self.assertIsNotNone(response.data['first_name'])
        self.assertIsNotNone(response.data['last_name'])
        self.assertIsNotNone(response.data['email'])

        # other users may NOT be read (they are just not found)
        response = self.client.get('%s%i/' % (self.USERS_BASEURL, u2.pk))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_user_read_list(self):
        """
            When a user requests the user list, they will only get their own in return.
        """
        u1, u2, u3 = TestModelUtils.create_user(), TestModelUtils.create_user(), TestModelUtils.create_user()

        self.set_api_client(u1)

        response = self.client.get(self.USERS_BASEURL)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(1, len(response.data))

    def test_user_read_admin(self):
        """
            admins may read all user details, even of different users
        """
        u1, u2 = TestModelUtils.create_user(), TestModelUtils.create_user()

        self.create_test_user(name=u1.username, admin=True)

        users_list = self.client.get(self.USERS_BASEURL).data
        self.assertEqual(len(users_list), 2)

        response = self.client.get('%s%i/' % (self.USERS_BASEURL, u2.pk))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['username'], u2.username)
        self.assertEqual(response.data['first_name'], u2.first_name)
        self.assertEqual(response.data['last_name'], u2.last_name)
        self.assertEqual(response.data['email'], u2.email)
        self.assertEqual(response.data['open_bettables'], u2.profile.get_open_bettables())

    def test_user_public_read(self):
        public_user = self.create_test_user(auth=False)
        response = self.client.get('%s%i/' % (self.USERS_BASEURL, public_user.pk))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_user_update_other_user_as_admin(self):
        u1 = self.create_test_user('u1')
        self.create_test_user('admin_user', admin=True)

        response = self.client.patch("%s%i/" % (self.USERS_BASEURL, u1.pk), {'username': 'newuser'}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        updated_user = User.objects.get(username='newuser')
        self.assertIsNotNone(updated_user)
        self.assertEqual(updated_user.username, 'newuser')
        self.assertRaises(User.DoesNotExist, User.objects.get, username='u1')

    def test_user_update_other_user_forbidden(self):
        u1 = self.create_test_user('u1')
        self.create_test_user('u2')

        response = self.client.patch("%s%i/" % (self.USERS_BASEURL, u1.pk), {'username': 'newuser'}, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_user_update_self(self):
        u1 = self.create_test_user('u1')
        response = self.client.patch("%s%i/" % (self.USERS_BASEURL, u1.pk),
                                     {'username': 'newuser', 'about': 'This is me!', 'location': 'Köln'},
                                     format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        updated_user = User.objects.get(username='newuser')
        self.assertIsNotNone(updated_user)
        self.assertEqual(updated_user.username, 'newuser')
        self.assertRaises(User.DoesNotExist, User.objects.get, username='u1')

    def test_user_update_self_profile_updates(self):
        u1 = self.create_test_user('u1')
        response = self.client.patch("%s%i/" % (self.USERS_BASEURL, u1.pk),
                                   {'email2': 'mail@mail2.de', 'location': 'Kölle', 'about': 'It\'s me',
                                    'avatar': None, 'reminder_emails': False}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        updated_profile = Profile.objects.get(pk=u1.pk)
        self.assertEqual('mail@mail2.de', updated_profile.email2)
        self.assertEqual('Kölle', updated_profile.location)
        self.assertEqual('It\'s me', updated_profile.about)
        self.assertFalse(updated_profile.reminder_emails)

    def test_user_update_username_valid(self):
        user = self.create_test_user()
        response = self.client.patch("%s%i/" % (self.USERS_BASEURL, user.pk),
                                     {'username': 'Hans im Glück', 'first_name': 'Hans', 'last_name': ''},
                                     format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        updated_user = User.objects.get(pk=user.pk)
        self.assertEqual('Hans', updated_user.first_name)
        self.assertEqual('', updated_user.last_name)

    def test_user_update_empty_fields(self):
        user = self.create_test_user()
        response = self.client.patch("%s%i/" % (self.USERS_BASEURL, user.pk),
                                     {'about': '', 'location': '', 'email2': ''}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_user_update_username_too_short(self):
        user = self.create_test_user()
        response = self.client.patch("%s%i/" % (self.USERS_BASEURL, user.pk), {'username': 'ei'}, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_user_update_username_invalid(self):
        user = self.create_test_user()
        response = self.client.patch("%s%i/" % (self.USERS_BASEURL, user.pk),
                                     {'username': 'semikolon;;;'}, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_user_update_first_name_too_long(self):
        user = self.create_test_user()
        response = self.client.patch("%s%i/" % (self.USERS_BASEURL, user.pk),
                                     {'first_name': 'aaaaaaaaa max. 30 characters aaaaaaaaaaaaaaaaaaaaaaaa'},
                                     format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_user_update_public(self):
        u1 = self.create_test_user('u1', auth=False)
        response = self.client.patch("%s%i/" % (self.USERS_BASEURL, u1.pk),
                                     {'username': 'newuser', 'location': 'Buxtehude'}, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_admin_update_user_has_paid_valid(self):
        """
            Admins may patch any user
        """
        self.create_test_user(admin=True)
        some_user = TestModelUtils.create_user()

        response = self.client.patch("%s%i/" % (self.ADMIN_USERS_BASEURL, some_user.pk),
                                     {'has_paid': 'true'}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        updated_user = User.objects.get(pk=some_user.pk)
        self.assertEqual(True, updated_user.profile.has_paid)

    def test_user_update_user_has_paid_failure(self):
        """
            Normal users may not patch a different user
        """
        self.create_test_user()
        some_user = TestModelUtils.create_user()

        response = self.client.patch("%s%i/" % (self.ADMIN_USERS_BASEURL, some_user.pk),
                                     {'has_paid': 'true'}, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        updated_user = User.objects.get(pk=some_user.pk)
        self.assertEqual(False, updated_user.profile.has_paid)

    def test_user_delete_other_user_not_found(self):
        """
            A user attempting to delete another user will get a 404 because the User view set
            will not even allow the user to see the other user, let alone deleting them.
        """
        self.create_test_user()
        some_other_user = TestModelUtils.create_user()
        response = self.client.delete("%s%i/" % (self.USERS_BASEURL, some_other_user.pk))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_user_delete_self_ok(self):
        user = self.create_test_user()
        response = self.client.delete("%s%i/" % (self.USERS_BASEURL, user.pk))
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_admin_delete_user_ok(self):
        self.create_test_user(admin=True)
        some_other_user = TestModelUtils.create_user()
        response = self.client.delete("%s%i/" % (self.USERS_BASEURL, some_other_user.pk))
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def create_test_user_api(self):
        return self.client.post(self.USERS_BASEURL, {'username': 'test_user_api', 'first_name': 'Testy',
                                                     'last_name': 'McTestface', 'email': 'test_user@test.de'},
                                format='json')
