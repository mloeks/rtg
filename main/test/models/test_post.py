# -*- coding: utf-8 -*-
from datetime import timedelta

from django.core.exceptions import ValidationError
from django.db import transaction
from django.db.utils import IntegrityError
from django.test import TestCase
from django.utils import timezone

from main.models import Post
from main.test.utils import TestModelUtils as utils


class PostTests(TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        Post.objects.all().delete()
        utils.cleanup()

    def test_to_string(self):
        u = utils.create_user('the queen')
        p = Post.objects.create(content='Tolle Neuigkeiten!', author=u)
        self.assertEqual('Post by the queen', str(p))

    def test_date_created(self):
        p = utils.create_post()
        date_format = '%d-%m-%y %H:%M:%S'
        self.assertTrue(p.date_created.strftime(date_format) == timezone.now().strftime(date_format))

        # auto_now can *not* be overriden!
        other_time = utils.create_datetime_from_now(timedelta(days=2, hours=1))
        p = Post.objects.create(content='foo', author=utils.create_user(), date_created=other_time)
        self.assertTrue(p.date_created.strftime(date_format) == timezone.now().strftime(date_format))