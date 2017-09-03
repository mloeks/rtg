# -*- coding: utf-8 -*-
import json

from django.contrib.auth.models import User
from rest_framework import status

from main.test.api.abstract_rtg_api_test import RtgApiTestCase
from main.test.utils import TestModelUtils


class UserApiTests(RtgApiTestCase):
    """
        Users are read_only via the API, except for updates of the own user
    """

    def setUp(self):
        User.objects.all().delete()

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
        """
            If a user attempts to update a different user, they will just get a 404, because they cannot access
            the resource of the other user
        """
        u1 = self.create_test_user('u1')
        self.create_test_user('u2')

        response = self.client.patch("%s%i/" % (self.USERS_BASEURL, u1.pk), {'username': 'newuser'}, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_user_update_self(self):
        u1 = self.create_test_user('u1')
        response = self.client.patch("%s%i/" % (self.USERS_BASEURL, u1.pk),
                                     {'username': 'newuser'},
                                     format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        updated_user = User.objects.get(username='newuser')
        self.assertIsNotNone(updated_user)
        self.assertEqual(updated_user.username, 'newuser')
        self.assertRaises(User.DoesNotExist, User.objects.get, username='u1')

    def test_user_update_public(self):
        u1 = self.create_test_user('u1', auth=False)
        response = self.client.patch("%s%i/" % (self.USERS_BASEURL, u1.pk), {'username': 'newuser'}, format='json')
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
        return self.client.post(self.USERS_BASEURL, {'username': 'test_user_api', 'first_name': 'Testy',
                                                     'last_name': 'McTestface', 'email': 'test_user@test.de'},
                                format='json')

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