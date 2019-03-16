# -*- coding: utf-8 -*-
from datetime import timedelta

from django.utils import timezone
from rest_framework import status

from main.models import Extra
from main.test.api.abstract_rtg_api_test import RtgApiTestCase


class ExtraApiTests(RtgApiTestCase):

    def tearDown(self):
        pass

    def test_extra_create(self):
        self.create_test_user(admin=True)
        response = self.create_test_extra_api()
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Extra.objects.count(), 1)
        self.assertIsNotNone(Extra.objects.get(name='Extrawurst'))

    def test_extra_create_unauth(self):
        self.create_test_user()
        response = self.create_test_extra_api()
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_extra_read(self):
        self.create_test_user()
        response = self.get_test_extra_api()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Extra.objects.count(), 1)
        self.assertIsNotNone(Extra.objects.get(name='Extrawurst'))

    def test_extra_public_read(self):
        self.create_test_user(auth=False)
        response = self.get_test_extra_api()
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_extra_update(self):
        self.create_test_user(admin=True)
        response = self.update_test_extra_api()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Extra.objects.count(), 1)

        stored_extra = list(Extra.objects.all()[:1])[0]
        self.assertIsNotNone(stored_extra)
        self.assertEquals(stored_extra.name, 'Sonderbehandlung')
        self.assertEquals(stored_extra.points, 101)
        self.assertRaises(Extra.DoesNotExist, Extra.objects.get, name='Extrawurst')

    def test_extra_update_unauth(self):
        self.create_test_user()
        response = self.update_test_extra_api()
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_extra_delete(self):
        self.create_test_user(admin=True)
        response = self.delete_test_extra_api()
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Extra.objects.count(), 0)

    def test_extra_delete_unauth(self):
        self.create_test_user()
        response = self.delete_test_extra_api()
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_extra_delete_public(self):
        self.create_test_user(auth=False)
        response = self.delete_test_extra_api()
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    @staticmethod
    def create_test_extra():
        try:
            test_extra = Extra.objects.get(name='Extrawurst')
        except Extra.DoesNotExist:
            test_extra = Extra(name='Extrawurst', points=100,
                               deadline=timezone.now() + timedelta(days=5), result='Salami')
            test_extra.save()
        return test_extra

    def get_test_extra_api(self):
        test_extra = self.create_test_extra()
        return self.client.get('%s%i/' % (self.EXTRAS_BASEURL, test_extra.pk))

    def create_test_extra_api(self):
        return self.client.post(self.EXTRAS_BASEURL,
                                {'name': 'Extrawurst', 'points': 100, 'deadline': '2016-06-06 18:00:00+0000',
                                 'result': 'Salami'}, format='json')

    def update_test_extra_api(self):
        test_extra = self.create_test_extra()
        return self.client.put("%s%i/" % (self.EXTRAS_BASEURL, test_extra.pk),
                               {'name': 'Sonderbehandlung', 'points': 101, 'deadline': '2016-08-08 20:00:00+0000',
                                'result': 'Schinkenwurst'}, format='json')

    def delete_test_extra_api(self):
        test_extra = self.create_test_extra()
        return self.client.delete("%s%i/" % (self.EXTRAS_BASEURL, test_extra.pk))