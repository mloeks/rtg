# -*- coding: utf-8 -*-

from django.contrib.auth.models import User
from rest_framework import status

from main.models import Post, Comment
from main.test.api.abstract_rtg_api_test import RtgApiTestCase
from test.utils import TestModelUtils


class CommentApiTests(RtgApiTestCase):

    def setUp(self):
        User.objects.all().delete()
        Post.objects.all().delete()
        Comment.objects.all().delete()

    def test_create(self):
        user = self.create_test_user()
        test_post = TestModelUtils.create_post('content', user)
        response = self.create_test_comment_api(user, test_post)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Comment.objects.count(), 1)
        self.assertIsNotNone(Comment.objects.get(author=user))

    def create_test_comment_api(self, author, post, reply_to_comment=None):
        return self.client.post(self.COMMENTS_BASEURL, {'content': 'content', 'author': author.pk, 'post': post.pk,
                                                        'reply_to': reply_to_comment}, format='json')
