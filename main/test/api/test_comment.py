# -*- coding: utf-8 -*-

from django.contrib.auth.models import User
from rest_framework import status

from main.models import Post, Comment
from main.test.api.abstract_rtg_api_test import RtgApiTestCase
from main.test.utils import TestModelUtils


class CommentApiTests(RtgApiTestCase):

    def setUp(self):
        User.objects.all().delete()
        Post.objects.all().delete()
        Comment.objects.all().delete()

    def test_create(self):
        user = self.create_test_user()
        test_post = TestModelUtils.create_post('content', TestModelUtils.create_user())
        response = self.create_test_comment_api(test_post)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Comment.objects.count(), 1)
        self.assertIsNotNone(Comment.objects.get(author=user))

    def test_delete_admin_other_comments(self):
        self.create_test_user(admin=True)

        test_post = TestModelUtils.create_post('content', TestModelUtils.create_user())
        test_comment_different_author = TestModelUtils.create_comment(author=TestModelUtils.create_user(), post=test_post)
        response = self.delete_comment_api(test_comment_different_author)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Comment.objects.count(), 0)

    def test_delete_failure_non_admin(self):
        user = self.create_test_user(admin=False)

        test_post = TestModelUtils.create_post('content', user)
        own_test_comment = TestModelUtils.create_comment(author=user, post=test_post,
                                                         reply_to=TestModelUtils.create_comment())
        response = self.delete_comment_api(own_test_comment)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(Comment.objects.count(), 2)

    def test_mark_removed_admin(self):
        self.create_test_user(admin=True)

        test_post = TestModelUtils.create_post('content', TestModelUtils.create_user())
        test_comment = TestModelUtils.create_comment(author=TestModelUtils.create_user(), post=test_post)
        response = self.client.patch('%s%s/' % (self.COMMENTS_BASEURL, test_comment.pk),
                                     {'removed': True}, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Comment.objects.count(), 1)
        self.assertTrue(Comment.objects.get(pk=test_comment.pk).removed)

    def create_test_comment_api(self, post, reply_to_comment=None):
        return self.client.post(self.COMMENTS_BASEURL, {'content': 'content', 'post': post.pk,
                                                        'reply_to': reply_to_comment}, format='json')

    def delete_comment_api(self, comment):
        return self.client.delete('%s%s/' % (self.COMMENTS_BASEURL, comment.pk))
