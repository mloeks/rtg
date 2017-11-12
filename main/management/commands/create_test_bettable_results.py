# -*- coding: utf-8 -*-
import random
from random import randrange

from django.core.management.base import BaseCommand

from main.models import Game, Bettable, ExtraChoice


class Command(BaseCommand):
    help = 'Creates random game results for the given percentage of all games'

    def add_arguments(self, parser):
        parser.add_argument('bettable_percentage')

    def handle(self, *args, **options):
        bettable_percentage = 0.01*float(options['bettable_percentage']) or 0.1

        self.reset_results()
        self.create_bettable_results(bettable_percentage)

    def reset_results(self):
        for bettable in Bettable.objects.all():
            if hasattr(bettable, 'game'):
                bettable.game.homegoals = -1
                bettable.game.awaygoals = -1
                bettable.game.save()
            bettable.result = None
            bettable.save()

    def create_bettable_results(self, bettable_percentage):
        nr_bettables = Bettable.objects.count()
        bettable_ct_to_generate_bets = int(bettable_percentage * nr_bettables)
        print("Generating random results for %i of %i bettables..." % (bettable_ct_to_generate_bets, nr_bettables))

        for bettable in Bettable.objects.all().order_by('?')[:bettable_ct_to_generate_bets]:
            if hasattr(bettable, 'game'):
                bettable.game.homegoals = randrange(5)
                bettable.game.awaygoals = randrange(5)
                bettable.game.save()
            elif hasattr(bettable, 'extra'):
                extra_choices = ExtraChoice.objects.filter(extra=bettable)
                bettable.result = str(random.choice(extra_choices))
                bettable.save()