# -*- coding: utf-8 -*-
from datetime import datetime, timedelta

from django.test import TestCase

from main.models import Game, Bet, Bettable
from main.test.utils import TestModelUtils as utils


class BettableTests(TestCase):

    def setUp(self):
        Bettable.objects.all().delete()
        Game.objects.all().delete()
        Bet.objects.all().delete()

    def test_get_open_bettables(self):
        u1, u2 = utils.create_user(), utils.create_user()
        g1, g2, g3 = utils.create_game(name="g1", deadline=datetime.now() - timedelta(hours=2)), \
                     utils.create_game(name="g2", deadline=datetime.now() + timedelta(minutes=5)), \
                     utils.create_game(name="g3", deadline=datetime.now() + timedelta(days=1))

        utils.create_bet(u1, g1, "2:1")
        utils.create_bet(u1, g3)
        utils.create_bet(u2, g1, "0:0")
        utils.create_bet(u2, g2, "0:3")

        self.assertEquals([g2, g3], BettableTests.children(Bettable.get_open_bettables_for_user(u1.pk)))
        self.assertEquals([g3], BettableTests.children(Bettable.get_open_bettables_for_user(u2.pk)))

    @staticmethod
    def children(bettables_list):
        return [bettable.get_related_child() for bettable in bettables_list]