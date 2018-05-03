# -*- coding: utf-8 -*-

from django.contrib.auth.models import User
from django.db import transaction
from django.db.utils import IntegrityError
from django.test import TestCase

from main.models import Profile
from main.test.utils import TestModelUtils as utils


class ProfileTests(TestCase):

    def test_to_string(self):
        u = utils.create_user('Queen')
        p = Profile.objects.get(user=u)

        self.assertEqual("Queen's Profile", str(p))

    def test_ordering(self):
        # TODO P3 case-insensitive ordering does not work with Meta class
        u1, u2, u3 = utils.create_user('Tick'), utils.create_user('zack'), utils.create_user('Track')

        profiles = list(Profile.objects.all())
        self.assertListEqual([u1, u2, u3], [p.user for p in profiles])

    def test_invalid_missing_fields(self):
        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                Profile.objects.create(user=None)

    def test_create_profile_after_user(self):
        User.objects.create(username='fipsy', first_name='John', last_name='Doe')
        user = User.objects.get(username='fipsy')
        self.assertEqual('fipsy', user.username)
        self.assertIsNotNone(user.profile)

        profile = Profile.objects.get(user__username='fipsy')
        self.assertIsNotNone(profile)
        self.assertEqual(user, profile.user)
        self.assertEqual(profile, user.profile)
        self.assertEqual('John', profile.user.first_name)
        self.assertEqual('Doe', profile.user.last_name)

    def test_get_display_name(self):
        User.objects.create(username='fipsy', first_name='John', last_name='Doe')
        profile = Profile.objects.get(user__username='fipsy')
        self.assertEqual('John Doe', profile.get_display_name())

        User.objects.create(username='fapsy')
        profile = Profile.objects.get(user__username='fapsy')
        self.assertEqual('fapsy', profile.get_display_name())

    def test_calculate_statistics(self):
        # TODO
        pass