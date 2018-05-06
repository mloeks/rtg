# -*- coding: utf-8 -*-
from django.contrib.auth.models import User
from django.core.management.base import BaseCommand

from main.models import Profile, Statistic


class Command(BaseCommand):
    help = 'Creates Profile and Statistic objects for all Users - if they do not exist yet'

    def handle(self, *args, **options):
        users = User.objects.all()

        for user in users:
            if not Profile.objects.filter(user=user).exists():
                print("Creating Profile for user %s" % user.username)
                Profile.objects.create(user=user)

            if not Statistic.objects.filter(user=user).exists():
                print("Creating Statistic for user %s" % user.username)
                Statistic.objects.create(user=user)




