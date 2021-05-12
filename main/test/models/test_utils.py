# -*- coding: utf-8 -*-
from datetime import timedelta

from django.test import TestCase
from django.utils import timezone

from main.models import User
from main.utils import active_users, inactive_users, extract_goals_from_result
from main.test.utils import TestModelUtils as utils


class UtilTests(TestCase):
    def setUp(self):
        User.objects.all().delete()

    def test_goals_from_string(self):
        self.assertEqual((3, 4), extract_goals_from_result('3:4'))
        self.assertEqual((0, 0), extract_goals_from_result('0:0'))
        self.assertEqual((-1, -1), extract_goals_from_result('-:-'))

    def test_active_users(self):
        u_active = utils.create_user(active=True, last_login=timezone.now())
        u_inactive_deactivated = utils.create_user(username='deactivated', active=False, last_login=timezone.now())
        u_inactive_never_logged_in = utils.create_user(username='never logged in', active=True, last_login=None)
        u_inactive_not_logged_in_this_year = utils.create_user(username='not logged in recently', \
                active=True, last_login=utils.create_datetime_from_now(timedelta(days=-365)))

        active = active_users()
        inactive = inactive_users()

        self.assertEquals(1, len(active))
        self.assertIn(u_active, active)

        self.assertEquals(3, len(inactive))
        self.assertNotIn(u_active, inactive)
