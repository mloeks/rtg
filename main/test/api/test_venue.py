# -*- coding: utf-8 -*-

from rest_framework import status

from main.models import Venue
from main.test.api.abstract_rtg_api_test import RtgApiTestCase


class VenueApiTests(RtgApiTestCase):

    def tearDown(self):
        self.delete_test_venue()

    def test_venue_create(self):
        self.create_test_user(admin=True)
        response = self.create_test_venue_api()
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Venue.objects.count(), 1)
        self.assertIsNotNone(Venue.objects.get(name='RTG National Stadium'))

    def test_venue_create_unauth(self):
        self.create_test_user()
        response = self.create_test_venue_api()
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_venue_read(self):
        self.create_test_user()
        response = self.get_test_venue_api()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Venue.objects.count(), 1)
        self.assertIsNotNone(Venue.objects.get(name='RTG National Stadium'))

    def test_venue_public_read(self):
        self.create_test_user(auth=False)
        response = self.get_test_venue_api()
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_venue_update(self):
        self.create_test_user(admin=True)
        response = self.update_test_venue_api()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Venue.objects.count(), 1)
        self.assertIsNotNone(Venue.objects.get(name='RTG Regional Field'))
        self.assertRaises(Venue.DoesNotExist, Venue.objects.get, name='RTG National Stadium')

    def test_venue_update_unauth(self):
        self.create_test_user()
        response = self.update_test_venue_api()
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_venue_delete(self):
        self.create_test_user(admin=True)
        response = self.delete_test_venue_api()
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Venue.objects.count(), 0)

    def test_venue_delete_unauth(self):
        self.create_test_user()
        response = self.delete_test_venue_api()
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_venue_delete_public(self):
        self.create_test_user(auth=False)
        response = self.delete_test_venue_api()
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    @staticmethod
    def create_test_venue():
        try:
            test_venue = Venue.objects.get(name='RTG National Stadium')
        except Venue.DoesNotExist:
            test_venue = Venue(name='RTG National Stadium', city='Glamour City', capacity=90000)
            test_venue.save()
        return test_venue

    @staticmethod
    def delete_test_venue():
        try:
            test_venue = Venue.objects.get(name='RTG National Stadium')
            test_venue.delete()
        except Venue.DoesNotExist:
            pass

    def get_test_venue_api(self):
        self.create_test_venue()
        venue_pk = Venue.objects.get(name='RTG National Stadium').pk
        return self.client.get('%s%i/' % (self.VENUES_BASEURL, venue_pk))

    def create_test_venue_api(self):
        return self.client.post(self.VENUES_BASEURL, {'name': 'RTG National Stadium', 'city': 'Glamour City',
                                                      'capacity': 90000}, format='json')

    def update_test_venue_api(self):
        self.create_test_venue()
        venue_pk = Venue.objects.get(name='RTG National Stadium').pk
        return self.client.put("%s%i/" % (self.VENUES_BASEURL, venue_pk),
                               {'name': 'RTG Regional Field', 'city': 'Simplicity Valley',
                                'capacity': 1909}, format='json')

    def delete_test_venue_api(self):
        self.create_test_venue()
        venue_pk = Venue.objects.get(name='RTG National Stadium').pk
        return self.client.delete("%s%i/" % (self.VENUES_BASEURL, venue_pk))