# -*- coding: utf-8 -*-

from django.contrib.auth.models import User
from rest_framework import status

from main.models import Post
from main.test.api.abstract_rtg_api_test import RtgApiTestCase


class PostApiTests(RtgApiTestCase):

    def setUp(self):
        User.objects.all().delete()
        Post.objects.all().delete()

    def test_post_create_admin(self):
        admin_user = self.create_test_user(admin=True)
        response = self.create_test_post_api(admin_user)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Post.objects.count(), 1)
        self.assertIsNotNone(Post.objects.get(author=admin_user))

    def test_post_fail_non_admin(self):
        user = self.create_test_user(admin=False)
        response = self.create_test_post_api(user)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(Post.objects.count(), 0)

    def delete_post_admin(self):
        admin_user = self.create_test_user(admin=True)

        test_post = Post(title='title', content='content', author=admin_user).save()
        self.assertEqual(Post.objects.count(), 1)

        response = self.client.delete("%s%i/" % (self.POSTS_BASEURL, test_post.pk))
        self.assertEqual(status.HTTP_204_NO_CONTENT, response)

    def delete_post_fail_non_admin(self):
        user = self.create_test_user(admin=False)

        test_post = Post(title='title', content='content', author=user).save()
        self.assertEqual(Post.objects.count(), 1)

        response = self.client.delete("%s%i/" % (self.POSTS_BASEURL, test_post.pk))
        self.assertEqual(status.HTTP_403_FORBIDDEN, response)

    def create_test_post_api(self, author):
        return self.client.post(self.POSTS_BASEURL, {'title': 'Title', 'content': 'content', 'author': author.pk},
                                format='json')
