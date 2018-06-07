# -*- coding: utf-8 -*-
from unittest import TestCase
from main.utils import extract_goals_from_result


class UtilTests(TestCase):
    def test_goals_from_string(self):
        self.assertEqual((3, 4), extract_goals_from_result('3:4'))
        self.assertEqual((0, 0), extract_goals_from_result('0:0'))
        self.assertEqual((-1, -1), extract_goals_from_result('-:-'))
