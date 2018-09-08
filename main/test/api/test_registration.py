# -*- coding: utf-8 -*-
from django.contrib.auth.models import User
from rest_framework.status import HTTP_200_OK, HTTP_400_BAD_REQUEST

from main.models import Profile
from main.test.api.abstract_rtg_api_test import RtgApiTestCase


class RegistrationApiTests(RtgApiTestCase):

    def setUp(self):
        User.objects.all().delete()
        Profile.objects.all().delete()

    def test_register_valid_user(self):
        register_payload = {
            'username': 'Her Royal Highness', 'first_name': 'Margaret', 'last_name': 'Windsor',
            'password': 'shirley1', 'password2': 'shirley1', 'email': 'hrh@windsor.co.uk'
        }
        response = self.client.post(self.REGISTER_URL, register_payload, format='json')
        self.assertEqual(HTTP_200_OK, response.status_code)
        self.assertTrue('access' in response.data)
        self.assertTrue('refresh' in response.data)

    def test_register_invalid_user_with_invalid_email(self):
        register_payload = {
            'username': 'Her Royal Highness', 'first_name': 'Margaret', 'last_name': 'Windsor',
            'password': 'shirley1', 'password2': 'shirley1', 'email': 'nomail'
        }
        response = self.client.post(self.REGISTER_URL, register_payload, format='json')
        self.assertEqual(HTTP_400_BAD_REQUEST, response.status_code)
        self.assertTrue('email' in response.data)

    def test_register_invalid_user_with_invalid_password(self):
        register_payload = {
            'username': 'Her Royal Highness', 'first_name': 'Margaret', 'last_name': 'Windsor',
            'password': 'short', 'password2': 'short', 'email': 'hrh@windsor.co.uk'
        }
        response = self.client.post(self.REGISTER_URL, register_payload, format='json')
        self.assertEqual(HTTP_400_BAD_REQUEST, response.status_code)
        # Unfortunately, the RegisterSerializer validates the password1/password2 fields and returns errors for these
        # fields accordingly
        self.assertTrue('password1' in response.data)

    def test_register_invalid_user_with_non_matching_passwords(self):
        register_payload = {
            'username': 'Her Royal Highness', 'first_name': 'Margaret', 'last_name': 'Windsor',
            'password': 'shirley1', 'password2': 'shirley2', 'email': 'hrh@windsor.co.uk'
        }
        response = self.client.post(self.REGISTER_URL, register_payload, format='json')
        self.assertEqual(HTTP_400_BAD_REQUEST, response.status_code)
        self.assertTrue('non_field_errors' in response.data)
