# -*- coding: utf-8 -*-
import random

from django.contrib.auth.models import User
from django.core.management.base import BaseCommand
from main.test.utils import TestModelUtils

from main.models import Post, Comment


class Command(BaseCommand):
    help = 'Creates a given number of test comments and twice as much replies to comments'

    def add_arguments(self, parser):
        parser.add_argument('number_comments')

    def handle(self, *args, **options):
        nr_comments = int(options['number_comments']) or 10

        self.clear_data()
        self.create_comments(nr_comments)
        self.create_replies(2 * nr_comments)

    def clear_data(self):
        Comment.objects.all().delete()

    def create_comments(self, number):
        for i in range(1, number+1):
            random_author = random.choice(list(User.objects.all()))
            random_post = random.choice(list(Post.objects.all()))
            Comment.objects.create(author=random_author, content=TestModelUtils.create_random_string(50),
                                   post=random_post)

    def create_replies(self, number):
        for i in range(1, number+1):
            random_author = random.choice(list(User.objects.all()))
            random_comment = random.choice(list(Comment.objects.all()))
            Comment.objects.create(author=random_author, content=TestModelUtils.create_random_string(50),
                                   post=random_comment.post, reply_to=random_comment)
