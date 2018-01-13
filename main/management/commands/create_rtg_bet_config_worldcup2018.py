# -*- coding: utf-8 -*-

from django.core.management.base import BaseCommand

from main.models import Extra
from main.models import ExtraChoice


class Command(BaseCommand):
    help = 'Creates RTG bet configuration for the World Cup 2018'

    def handle(self, *args, **options):
        self.clear_data()
        self.extras = self.create_extras()
        self.create_extrachoices()

    def clear_data(self):
        Extra.objects.all().delete()
        ExtraChoice.objects.all().delete()
        
    def create_extras(self):
        extras = {
            'weltmeister': Extra(name='Wer wird Weltmeister?', points=10, deadline='2018-06-14 17:00:00+02'),
            'deutschland': Extra(name='Wie weit kommt Deutschland?', points=5, deadline='2018-06-14 17:00:00+02')
        }
        
        for key, extra in extras.items():
            extra.save()
        return extras
    
    def create_extrachoices(self):
        ExtraChoice(name='Vorrunde', sort_index='010', extra=self.extras['deutschland']).save()
        ExtraChoice(name='Achtelfinale', sort_index='020', extra=self.extras['deutschland']).save()
        ExtraChoice(name='Viertelfinale', sort_index='030', extra=self.extras['deutschland']).save()
        ExtraChoice(name='Halbfinale', sort_index='040', extra=self.extras['deutschland']).save()
        ExtraChoice(name='Zweiter', sort_index='050', extra=self.extras['deutschland']).save()
        ExtraChoice(name='Weltmeister', sort_index='060', extra=self.extras['deutschland']).save()

        # ExtraChoice(name='Frankreich', extra=self.extras['weltmeister']).save()
        # TODO insert all other teams
