# -*- coding: utf-8 -*-

from rest_framework import status

from main.models import ExtraChoice
from main.test.api.abstract_rtg_api_test import RtgApiTestCase
from main.test.api.test_extra import ExtraApiTests


class ExtraChoiceApiTests(RtgApiTestCase):

    def tearDown(self):
        pass

    def test_extrachoice_create(self):
        self.create_test_user(admin=True)
        response = self.create_test_extrachoice_api()
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(ExtraChoice.objects.count(), 1)
        self.assertIsNotNone(ExtraChoice.objects.get(name='Salami'))

    def test_extrachoice_create_unauth(self):
        self.create_test_user()
        response = self.create_test_extrachoice_api()
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_extrachoice_read(self):
        self.create_test_user()
        response = self.get_test_extrachoice_api()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(ExtraChoice.objects.count(), 1)
        self.assertIsNotNone(ExtraChoice.objects.get(name='Salami'))

    def test_extrachoice_public_read(self):
        self.create_test_user(auth=False)
        response = self.get_test_extrachoice_api()
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_extrachoice_update(self):
        self.create_test_user(admin=True)
        response = self.update_test_extrachoice_api()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(ExtraChoice.objects.count(), 1)

        stored_extrachoice = list(ExtraChoice.objects.all()[:1])[0]
        self.assertIsNotNone(stored_extrachoice)
        self.assertEquals(stored_extrachoice.name, 'Schinkenwurst')
        self.assertEquals(stored_extrachoice.sort_index, '456')
        self.assertRaises(ExtraChoice.DoesNotExist, ExtraChoice.objects.get, name='Salami')

    def test_extrachoice_update_unauth(self):
        self.create_test_user()
        response = self.update_test_extrachoice_api()
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_extrachoice_delete(self):
        self.create_test_user(admin=True)
        response = self.delete_test_extrachoice_api()
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(ExtraChoice.objects.count(), 0)

    def test_extrachoice_delete_unauth(self):
        self.create_test_user()
        response = self.delete_test_extrachoice_api()
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_extrachoice_delete_public(self):
        self.create_test_user(auth=False)
        response = self.delete_test_extrachoice_api()
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    @staticmethod
    def create_test_extrachoice():
        try:
            test_extrachoice = ExtraChoice.objects.get(name='Salami')
        except ExtraChoice.DoesNotExist:
            test_extra = ExtraApiTests.create_test_extra()
            test_extrachoice = ExtraChoice(name='Salami', extra=test_extra, sort_index='123')
            test_extrachoice.save()
        return test_extrachoice

    def get_test_extrachoice_api(self):
        test_extrachoice = self.create_test_extrachoice()
        return self.client.get('%s%i/' % (self.EXTRACHOICES_BASEURL, test_extrachoice.pk))

    def create_test_extrachoice_api(self):
        test_extra = ExtraApiTests.create_test_extra()
        return self.client.post(self.EXTRACHOICES_BASEURL,
                                {'name': 'Salami', 'extra': test_extra.pk, 'sort_index': '123'}, format='json')

    def update_test_extrachoice_api(self):
        test_extra = ExtraApiTests.create_test_extra()
        test_extrachoice = self.create_test_extrachoice()
        return self.client.put("%s%i/" % (self.EXTRACHOICES_BASEURL, test_extrachoice.pk),
                               {'name': 'Schinkenwurst', 'extra': test_extra.pk, 'sort_index': '456'}, format='json')

    def delete_test_extrachoice_api(self):
        test_extrachoice = self.create_test_extrachoice()
        return self.client.delete("%s%i/" % (self.EXTRACHOICES_BASEURL, test_extrachoice.pk))