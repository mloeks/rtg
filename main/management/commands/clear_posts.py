# -*- coding: utf-8 -*-

from django.core.management.base import BaseCommand

from main.models import Post


class Command(BaseCommand):
    help = 'Clears all posts and comments'

    def handle(self, *args, **options):
        Post.objects.all().delete()
        Comment.objects.all().delete()
