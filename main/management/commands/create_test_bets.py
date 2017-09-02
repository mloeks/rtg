# -*- coding: utf-8 -*-
from random import randrange

from django.contrib.auth.models import User
from django.core.management.base import BaseCommand

from main.models import GameBet, Game


class Command(BaseCommand):
    help = 'Creates random bets for the given percentage of all games for each available user'

    def add_arguments(self, parser):
        parser.add_argument('bet_percentage')

    def handle(self, *args, **options):
        bet_percentage = 0.01*float(options['bet_percentage']) or 0.1

        self.clear_data()
        self.create_bets(bet_percentage)

    def clear_data(self):
        GameBet.objects.all().delete()

    def create_bets(self, bet_percentage):
        nr_games = Game.objects.count()
        game_ct_to_generate_bets = int(bet_percentage*nr_games)
        print("Generating bets for %i of %i games..." % (game_ct_to_generate_bets, nr_games))

        for user in User.objects.all():
            for game in Game.objects.all().order_by('?')[:game_ct_to_generate_bets]:
                GameBet(user=user, game=game, homegoals=randrange(5), awaygoals=randrange(5)).save()