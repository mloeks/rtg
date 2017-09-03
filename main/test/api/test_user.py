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