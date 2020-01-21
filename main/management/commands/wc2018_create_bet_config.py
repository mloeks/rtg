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
        ExtraChoice(name='Vierter', sort_index='050', extra=self.extras['deutschland']).save()
        ExtraChoice(name='Dritter', sort_index='060', extra=self.extras['deutschland']).save()
        ExtraChoice(name='Zweiter', sort_index='070', extra=self.extras['deutschland']).save()
        ExtraChoice(name='Weltmeister', sort_index='080', extra=self.extras['deutschland']).save()

        self.new_weltmeister_choice('Ägypten')
        self.new_weltmeister_choice('Argentinien')
        self.new_weltmeister_choice('Australien')
        self.new_weltmeister_choice('Belgien')
        self.new_weltmeister_choice('Brasilien')
        self.new_weltmeister_choice('Costa Rica')
        self.new_weltmeister_choice('Dänemark')
        self.new_weltmeister_choice('Deutschland')
        self.new_weltmeister_choice('England')
        self.new_weltmeister_choice('Frankreich')
        self.new_weltmeister_choice('Iran')
        self.new_weltmeister_choice('Island')
        self.new_weltmeister_choice('Japan')
        self.new_weltmeister_choice('Kolumbien')
        self.new_weltmeister_choice('Kroatien')
        self.new_weltmeister_choice('Marokko')
        self.new_weltmeister_choice('Mexiko')
        self.new_weltmeister_choice('Nigeria')
        self.new_weltmeister_choice('Panama')
        self.new_weltmeister_choice('Peru')
        self.new_weltmeister_choice('Polen')
        self.new_weltmeister_choice('Portugal')
        self.new_weltmeister_choice('Russland')
        self.new_weltmeister_choice('Saudi-Arabien')
        self.new_weltmeister_choice('Schweden')
        self.new_weltmeister_choice('Schweiz')
        self.new_weltmeister_choice('Senegal')
        self.new_weltmeister_choice('Serbien')
        self.new_weltmeister_choice('Spanien')
        self.new_weltmeister_choice('Südkorea')
        self.new_weltmeister_choice('Tunesien')
        self.new_weltmeister_choice('Uruguay')

    def new_weltmeister_choice(self, name):
        ExtraChoice(name=name, extra=self.extras['weltmeister']).save()
