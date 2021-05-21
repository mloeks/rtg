# -*- coding: utf-8 -*-

from django.contrib.auth.models import User
from rest_framework import status

from main.models import Post
from main.test.api.abstract_rtg_api_test import RtgApiTestCase
from main.test.utils import TestModelUtils


class PostApiTests(RtgApiTestCase):

    def setUp(self):
        User.objects.all().delete()
        Post.objects.all().delete()

    def test_create_admin(self):
        admin_user = self.create_test_user(admin=True)
        response = self._create_test_post_api(admin_user)

        self.assertEqual(status.HTTP_201_CREATED, response.status_code)
        self.assertEqual(Post.objects.count(), 1)
        self.assertIsNotNone(Post.objects.get(author=admin_user))

    def test_create_non_admin(self):
        user = self.create_test_user(admin=False)
        response = self._create_test_post_api(user)

        self.assertEqual(status.HTTP_201_CREATED, response.status_code)
        self.assertEqual(Post.objects.count(), 1)
        self.assertIsNotNone(Post.objects.get(author=user))

    def test_create_admin_with_mail_options(self):
        admin_user = self.create_test_user(admin=True)

        self.assertEqual(status.HTTP_201_CREATED, self._create_test_post_with_mail_options(admin_user, True, False, False, False).status_code)
        self.assertEqual(status.HTTP_201_CREATED, self._create_test_post_with_mail_options(admin_user, False, True, False, False).status_code)
        self.assertEqual(status.HTTP_201_CREATED, self._create_test_post_with_mail_options(admin_user, False, False, True, False).status_code)
        self.assertEqual(status.HTTP_201_CREATED, self._create_test_post_with_mail_options(admin_user, False, False, False, True).status_code)
        self.assertEqual(Post.objects.count(), 4)

    def test_create_failure_non_admin_with_mail_options(self):
        user = self.create_test_user(admin=False)

        self.assertEqual(status.HTTP_403_FORBIDDEN, self._create_test_post_with_mail_options(user, False, False, False, False).status_code)
        self.assertEqual(status.HTTP_403_FORBIDDEN, self._create_test_post_with_mail_options(user, True, False, False, False).status_code)
        self.assertEqual(status.HTTP_403_FORBIDDEN, self._create_test_post_with_mail_options(user, False, True, False, False).status_code)
        self.assertEqual(status.HTTP_403_FORBIDDEN, self._create_test_post_with_mail_options(user, False, False, True, False).status_code)
        self.assertEqual(status.HTTP_403_FORBIDDEN, self._create_test_post_with_mail_options(user, False, False, False, True).status_code)
        self.assertEqual(status.HTTP_403_FORBIDDEN, self._create_test_post_with_mail_options(user, True, True, True, True).status_code)
        self.assertEqual(Post.objects.count(), 0)

    def test_create_failure_missing_content(self):
        user = self.create_test_user(admin=True)
        response = self._create_test_post_api(user, 'Title', '')
        self.assertEqual(status.HTTP_400_BAD_REQUEST, response.status_code)
        self.assertEqual(Post.objects.count(), 0)

    def test_create_failure_missing_title(self):
        user = self.create_test_user(admin=True)
        response = self._create_test_post_api(user, None, 'content')
        self.assertEqual(status.HTTP_400_BAD_REQUEST, response.status_code)
        self.assertEqual(Post.objects.count(), 0)

    def test_create_missing_title_in_draft(self):
        user = self.create_test_user(admin=True)
        response = self._create_test_post_api(user, '', 'content', False)
        self.assertEqual(status.HTTP_201_CREATED, response.status_code)
        self.assertEqual(Post.objects.count(), 1)

    def test_create_missing_content_in_draft(self):
        user = self.create_test_user(admin=True)
        response = self._create_test_post_api(user, 'Title', None, False)
        self.assertEqual(status.HTTP_201_CREATED, response.status_code)
        self.assertEqual(Post.objects.count(), 1)

    def test_delete_admin(self):
        admin_user = self.create_test_user(admin=True)

        test_post = TestModelUtils.create_post('content', admin_user)
        self.assertEqual(Post.objects.count(), 1)

        response = self.client.delete("%s%i/" % (self.POSTS_BASEURL, test_post.pk))
        self.assertEqual(status.HTTP_204_NO_CONTENT, response.status_code)

    def test_delete_failure_non_admin(self):
        user = self.create_test_user(admin=False)

        test_post = TestModelUtils.create_post('content', user)
        self.assertEqual(Post.objects.count(), 1)

        response = self.client.delete("%s%i/" % (self.POSTS_BASEURL, test_post.pk))
        self.assertEqual(status.HTTP_403_FORBIDDEN, response.status_code)

    def _create_test_post_api(self, author, title='Title', content='content', finished=True):
        return self.client.post(self.POSTS_BASEURL, {'title': title, 'content': content, 'author': author.pk,
                                                     'finished': finished}, format='json')

    def _create_test_post_with_mail_options(self, author, as_mail, force_active, force_inactive, force_all):
        return self.client.post(self.POSTS_BASEURL, {'title': 'some title', 'content': 'some content', 'author': author.pk,
                                                     'finished': True, 'as_mail': as_mail, 'force_active_users': force_active,
                                                     'force_inactive_users': force_inactive, 'force_all_users': force_all}, format='json')
