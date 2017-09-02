# -*- coding: utf-8 -*-
import random

from django.contrib.auth.models import User
from django.core.management.base import BaseCommand
from main.test.utils import TestModelUtils

from main.models import Post


class Command(BaseCommand):
    help = 'Creates a given number of test posts'

    def add_arguments(self, parser):
        parser.add_argument('number_posts')

    def handle(self, *args, **options):
        nr_posts = int(options['number_posts']) or 10

        self.clear_data()
        self.create_posts(nr_posts)

    def clear_data(self):
        Post.objects.all().delete()

    def create_posts(self, number):
        for i in range(1, number+1):
            random_author = random.choice(list(User.objects.all()))
            random_appear = random.choice([True, False])
            Post(author=random_author, title=TestModelUtils.create_random_string(40),
                 content=TestModelUtils.create_random_string(500), news_appear=random_appear).save()
