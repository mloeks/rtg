# -*- coding: utf-8 -*-

from django.contrib.auth.models import User
from django.core.management.base import BaseCommand

from main.models import Post


class Command(BaseCommand):
    help = 'Creates a given number of test users'

    def add_arguments(self, parser):
        parser.add_argument('number_users')

    def handle(self, *args, **options):
        nr_users = int(options['number_users']) or 7

        self.clear_data()
        self.create_users(nr_users)

    def clear_data(self):
        Post.objects.all().delete()
        User.objects.exclude(is_staff=True).delete()

    def create_users(self, number):
        for i in range(1, number+1):
            email_and_password = 'user%i@rtg.de' % i
            User.objects.create_user(username='User %i' % i, first_name='Ben', last_name='Utzer %i' % i,
                                     email=email_and_password, password=email_and_password)