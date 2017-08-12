# -*- coding: utf-8 -*-
from random import randrange

from django.contrib.auth.models import User
from django.core.management.base import BaseCommand

from rtg.models import GameBet, Game


class Command(BaseCommand):
    help = 'Creates random game results for the given percentage of all games'

    def add_arguments(self, parser):
        parser.add_argument('game_percentage')

    def handle(self, *args, **options):
        game_percentage = 0.01*float(options['game_percentage']) or 0.1

        self.clear_data()
        self.create_game_results(game_percentage)

    def clear_data(self):
        for game in Game.objects.all():
            game.homegoals = -1
            game.awaygoals = -1
            game.save()

    def create_game_results(self, game_percentage):
        nr_games = Game.objects.count()
        game_ct_to_generate_bets = int(game_percentage * nr_games)
        print("Generating random results for %i of %i games..." % (game_ct_to_generate_bets, nr_games))

        for game in Game.objects.all().order_by('?')[:game_ct_to_generate_bets]:
            game.homegoals = randrange(5)
            game.awaygoals = randrange(5)
            game.save()