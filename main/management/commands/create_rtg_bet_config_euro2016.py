# -*- coding: utf-8 -*-

from django.core.management.base import BaseCommand

from main.models import Extra
from main.models import ExtraChoice


class Command(BaseCommand):
    help = 'Creates RTG bet configuration'

    def handle(self, *args, **options):
        self.clear_data()
        self.extras = self.create_extras()
        self.create_extrachoices()

    def clear_data(self):
        Extra.objects.all().delete()
        ExtraChoice.objects.all().delete()
        
    def create_extras(self):
        extras = {
            'europameister': Extra(name='Wer wird Europameister?', points=10, deadline='2016-06-10 21:00:00+02'),
            'deutschland': Extra(name='Wie weit kommt Deutschland?', points=5, deadline='2016-06-10 21:00:00+02')
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
        ExtraChoice(name='Europameister', sort_index='060', extra=self.extras['deutschland']).save()

        ExtraChoice(name='Frankreich', extra=self.extras['europameister']).save()
        ExtraChoice(name='Rumänien', extra=self.extras['europameister']).save()
        ExtraChoice(name='Albanien', extra=self.extras['europameister']).save()
        ExtraChoice(name='Schweiz', extra=self.extras['europameister']).save()
        ExtraChoice(name='Wales', extra=self.extras['europameister']).save()
        ExtraChoice(name='Slowakei', extra=self.extras['europameister']).save()
        ExtraChoice(name='England', extra=self.extras['europameister']).save()
        ExtraChoice(name='Russland', extra=self.extras['europameister']).save()
        ExtraChoice(name='Türkei', extra=self.extras['europameister']).save()
        ExtraChoice(name='Kroatien', extra=self.extras['europameister']).save()
        ExtraChoice(name='Polen', extra=self.extras['europameister']).save()
        ExtraChoice(name='Nordirland', extra=self.extras['europameister']).save()
        ExtraChoice(name='Deutschland', extra=self.extras['europameister']).save()
        ExtraChoice(name='Ukraine', extra=self.extras['europameister']).save()
        ExtraChoice(name='Spanien', extra=self.extras['europameister']).save()
        ExtraChoice(name='Tschechien', extra=self.extras['europameister']).save()
        ExtraChoice(name='Irland', extra=self.extras['europameister']).save()
        ExtraChoice(name='Schweden', extra=self.extras['europameister']).save()
        ExtraChoice(name='Belgien', extra=self.extras['europameister']).save()
        ExtraChoice(name='Italien', extra=self.extras['europameister']).save()
        ExtraChoice(name='Österreich', extra=self.extras['europameister']).save()
        ExtraChoice(name='Ungarn', extra=self.extras['europameister']).save()
        ExtraChoice(name='Portugal', extra=self.extras['europameister']).save()
        ExtraChoice(name='Island', extra=self.extras['europameister']).save()
