# -*- coding: utf-8 -*-
from django.contrib.auth.models import User
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = 'Recalculates all points'

    def handle(self, *args, **options):
        for user in User.objects.all():
            user.statistic.recalculate()
            user.statistic.update_no_bets()
            user.statistic.save()