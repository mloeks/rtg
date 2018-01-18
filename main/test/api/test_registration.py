# -*- coding: utf-8 -*-
from django.contrib.auth.models import User
from rest_framework.status import HTTP_200_OK, HTTP_400_BAD_REQUEST

from main.models import Profile
from main.test.api.abstract_rtg_api_test import RtgApiTestCase


class RegistrationApiTests(RtgApiTestCase):

    def tearDown(self):
        User.objects.all().delete()
        Profile.objects.all().delete()

    def test_register_valid_user(self):
        register_payload = {
            'username': 'Her Royal Highness', 'email': 'hrh@windsor.co.uk', 'first_name': 'Margaret', 'last_name': 'Windsor',
            'password': 'shirley1', 'password1': 'shirley1', 'password2': 'shirley1'
        }
        response = self.client.post(self.REGISTER_URL, register_payload, format='json')
        self.assertEqual(HTTP_200_OK, response.status_code)
        self.assertTrue('token' in response.data)

    def test_register_invalid_user_with_field_error(self):
        """ Test that response contains a field_error for an invalid email """
        register_payload = {
            'username': 'Her Royal Highness', 'email': 'nomail', 'first_name': 'Margaret', 'last_name': 'Windsor',
            'password': 'shirley1', 'password1': 'shirley1', 'password2': 'shirley1'
        }
        response = self.client.post(self.REGISTER_URL, register_payload, format='json')
        self.assertEqual(HTTP_400_BAD_REQUEST, response.status_code)
        self.assertTrue('email' in response.data)

    def test_register_invalid_user_with_non_field_error(self):
        """ Test that response contains non_field_errors when both passwords are not identical. """
        register_payload = {
            'username': 'Her Royal Highness', 'email': 'hrh@windsor.co.uk', 'first_name': 'Margaret', 'last_name': 'Windsor',
            'password': 'shirley1', 'password1': 'shirley1', 'password2': 'shirley2'
        }
        response = self.client.post(self.REGISTER_URL, register_payload, format='json')
        self.assertEqual(HTTP_400_BAD_REQUEST, response.status_code)
        self.assertTrue('non_field_errors' in response.data)
