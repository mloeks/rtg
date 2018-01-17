# -*- coding: utf-8 -*-
from allauth.account.adapter import DefaultAccountAdapter
from django.core.exceptions import ValidationError
from django.test import TestCase


class RegistrationOverridesTest(TestCase):

    def setUp(self):
        self.adapter = DefaultAccountAdapter()

    def test_valid_usernames(self):
        try:
            self.adapter.clean_username('JürgenÜlfDrägör')
            self.adapter.clean_username('matze09')
            self.adapter.clean_username('Foo Bar')
            self.adapter.clean_username('matt@bratt')
            self.adapter.clean_username('Testy.Mc.Testface')
            self.adapter.clean_username('foo+bar')
            self.adapter.clean_username('foo-bar')
            self.adapter.clean_username('Dorothee_von_Schweden')
        except ValidationError:
            self.fail("ValidationError raised unexpectedly.")

    def test_invalid_usernames(self):
        with self.assertRaises(ValidationError):
            self.adapter.clean_username('ei')
            self.adapter.clean_username('drei€')
            self.adapter.clean_username('foo: bar')
            self.adapter.clean_username('Karl/Heinz')
            self.adapter.clean_username('Semi;')
