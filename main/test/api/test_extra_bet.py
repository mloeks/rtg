# -*- coding: utf-8 -*-
import json
from datetime import timedelta

from rest_framework import status

from main.models import ExtraBet
from main.test.api.abstract_rtg_api_test import RtgApiTestCase
from main.test.api.test_extra import ExtraApiTests
from main.test.utils import TestModelUtils


class ExtraBetApiTests(RtgApiTestCase):

    def tearDown(self):
        ExtraBet.objects.all().delete()

    def test_extrabet_create_admin(self):
        self.create_test_user(admin=True)
        response = self.create_test_extrabet_api()
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(ExtraBet.objects.count(), 1)
        self.assertIsNotNone(ExtraBet.objects.get(result_bet='Lyoner'))

    def test_extrabet_create(self):
        u1 = TestModelUtils.create_user()
        self.create_test_user(u1.username)
        response = self.create_test_extrabet_api()
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(ExtraBet.objects.count(), 1)
        self.assertIsNotNone(ExtraBet.objects.get(result_bet='Lyoner'))
        self.assertEqual(u1.pk, ExtraBet.objects.get(result_bet='Lyoner').user.id)

    def test_extrabet_create_public(self):
        self.create_test_user(auth=False)
        response = self.create_test_extrabet_api()
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_extrabet_read(self):
        # TODO apply restrictions when trying to read bets created by other users
        self.create_test_user()
        response = self.get_test_extrabet_api()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(ExtraBet.objects.count(), 1)
        self.assertIsNotNone(ExtraBet.objects.get(result_bet='Lyoner'))

    def test_extrabet_read_allowed(self):
        u1, u2 = TestModelUtils.create_user(), TestModelUtils.create_user()

        e1 = TestModelUtils.create_extra(deadline=TestModelUtils.create_datetime_from_now(timedelta(days=-2)))
        e2 = TestModelUtils.create_extra(deadline=TestModelUtils.create_datetime_from_now(timedelta(hours=5)))
        e3 = TestModelUtils.create_extra(deadline=TestModelUtils.create_datetime_from_now(timedelta(hours=-1)))
        e4 = TestModelUtils.create_extra(deadline=TestModelUtils.create_datetime_from_now(timedelta(days=12)))

        eb1 = TestModelUtils.create_extrabet('foo', e1, u1)
        eb2 = TestModelUtils.create_extrabet('bar', e2, u1)
        eb3 = TestModelUtils.create_extrabet('baz', e3, u1)

        eb5 = TestModelUtils.create_extrabet('bee', e4, u2)
        eb6 = TestModelUtils.create_extrabet('bling', e2, u2)
        eb7 = TestModelUtils.create_extrabet('blang', e1, u2)
        eb8 = TestModelUtils.create_extrabet('blong', e3, u2)

        # reply only those bets that are owned by the user or deadline has passed
        self.create_test_user(u1.username)
        response = list(self.client.get(self.EXTRABETS_BASEURL))[0]
        bets = json.loads(response)
        self.assertEqual(5, len(bets))
        self.assertEqual([eb.id for eb in [eb1, eb2, eb3, eb7, eb8]], [eb['id'] for eb in bets])

        self.create_test_user(u2.username)
        response = list(self.client.get(self.EXTRABETS_BASEURL))[0]
        bets = json.loads(response)
        self.assertEqual(6, len(bets))
        self.assertEqual([eb.id for eb in [eb1, eb3, eb5, eb6, eb7, eb8]], [eb['id'] for eb in bets])

    def test_extrabet_public_read(self):
        self.create_test_user(auth=False)
        response = self.get_test_extrabet_api()
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_extrabet_create_deadlines(self):
        """
            cf. GameBet test
        """
        u1 = TestModelUtils.create_user()

        e1 = TestModelUtils.create_extra()    # deadline is NOW
        e2 = TestModelUtils.create_extra(deadline=TestModelUtils.create_datetime_from_now(timedelta(hours=2)))

        self.create_test_user(u1.username)
        create_disallowed = self.client.post(self.EXTRABETS_BASEURL, {'result_bet': 'zilch', 'extra': e1.pk},
                                             format='json')
        self.assertEqual(status.HTTP_400_BAD_REQUEST, create_disallowed.status_code)

        create_allowed = self.client.post(self.EXTRABETS_BASEURL, {'result_bet': 'nuts', 'extra': e2.pk},
                                          format='json')
        self.assertEqual(status.HTTP_201_CREATED, create_allowed.status_code)

    def test_extrabet_create_other(self):
        """
            cf. GameBet test
        """
        u1, u2 = TestModelUtils.create_user(), TestModelUtils.create_user()

        e1 = TestModelUtils.create_extra(deadline=TestModelUtils.create_datetime_from_now(timedelta(hours=2)))  # bets open

        self.create_test_user(u2.username)
        create_unsuccessful = self.client.post(self.EXTRABETS_BASEURL, {'result_bet': 'blubb', 'extra': e1.pk,
                                                                        'user': u1.pk}, format='json')
        self.assertEqual(status.HTTP_201_CREATED, create_unsuccessful.status_code)
        self.assertEqual(u2.pk, ExtraBet.objects.get(extra__pk=e1.pk).user.id)        # user has been overwritten by self!

        ExtraBet.objects.all().delete()

        create_successful = self.client.post(self.EXTRABETS_BASEURL, {'result_bet': 'flapp', 'extra': e1.pk,
                                                                      'user': u2.pk}, format='json')
        self.assertEqual(status.HTTP_201_CREATED, create_successful.status_code)
        self.assertEqual(u2.pk, ExtraBet.objects.get(extra__pk=e1.pk).user.id)

    def test_extrabet_update_deadlines(self):
        """
            cf. GameBet test
        """
        u1 = TestModelUtils.create_user()

        e1 = TestModelUtils.create_extra()    # deadline is NOW
        e2 = TestModelUtils.create_extra(deadline=TestModelUtils.create_datetime_from_now(timedelta(hours=2)))

        eb1 = TestModelUtils.create_extrabet('fubu', e1, u1)
        eb2 = TestModelUtils.create_extrabet('faba', e2, u1)

        self.create_test_user(u1.username)
        update_disallowed = self.client.put("%s%i/" % (self.EXTRABETS_BASEURL, eb1.pk),
                                            {'result_bet': 'fibi', 'extra': e1.pk}, format='json')
        self.assertEqual(status.HTTP_400_BAD_REQUEST, update_disallowed.status_code)

        update_allowed = self.client.put("%s%i/" % (self.EXTRABETS_BASEURL, eb2.pk),
                                         {'result_bet': 'febe', 'extra': e2.pk}, format='json')
        self.assertEqual(status.HTTP_200_OK, update_allowed.status_code)

    def test_extrabet_update_other(self):
        """
            cf. GameBet test
        """
        u1, u2 = TestModelUtils.create_user(), TestModelUtils.create_user()

        e1 = TestModelUtils.create_extra(deadline=TestModelUtils.create_datetime_from_now(timedelta(hours=2)))  # bets open
        eb1 = TestModelUtils.create_extrabet('zonk', e1, u1)

        self.create_test_user(u2.username)
        update_disallowed = self.client.put("%s%i/" % (self.EXTRABETS_BASEURL, eb1.pk),
                                            {'result_bet': 'zink', 'extra': e1.pk}, format='json')
        self.assertEqual(status.HTTP_404_NOT_FOUND, update_disallowed.status_code)

    def test_extrabet_delete_other(self):
        """
            cf. GameBet test
        """
        u1, u2 = TestModelUtils.create_user(), TestModelUtils.create_user()

        e1 = TestModelUtils.create_extra(deadline=TestModelUtils.create_datetime_from_now(timedelta(hours=2)))  # bets open
        eb1 = TestModelUtils.create_extrabet('bummer', e1, u1)

        self.create_test_user(u2.username)
        delete_disallowed = self.client.delete("%s%i/" % (self.EXTRABETS_BASEURL, eb1.pk))
        self.assertEqual(status.HTTP_404_NOT_FOUND, delete_disallowed.status_code)

        self.create_test_user(u1.username)
        delete_disallowed = self.client.delete("%s%i/" % (self.EXTRABETS_BASEURL, eb1.pk))
        self.assertEqual(status.HTTP_204_NO_CONTENT, delete_disallowed.status_code)

    def test_extrabet_update(self):
        self.create_test_user()
        response = self.update_test_extrabet_api()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(ExtraBet.objects.count(), 1)

        stored_extrabet = list(ExtraBet.objects.all()[:1])[0]
        self.assertIsNotNone(stored_extrabet)
        self.assertEquals(stored_extrabet.result_bet, 'Paprikasalami')
        self.assertRaises(ExtraBet.DoesNotExist, ExtraBet.objects.get, result_bet='Lyoner')

    def test_extrabet_delete_admin(self):
        self.create_test_user(admin=True)
        response = self.delete_test_extrabet_api()
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(ExtraBet.objects.count(), 0)

    def test_extrabet_delete(self):
        self.create_test_user()
        response = self.delete_test_extrabet_api()
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_extrabet_delete_public(self):
        self.create_test_user(auth=False)
        response = self.delete_test_extrabet_api()
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    @staticmethod
    def create_test_extrabet(user):
        test_extra = ExtraApiTests.create_test_extra()
        test_extrabet = ExtraBet(result_bet='Lyoner', extra=test_extra, user=user)
        test_extrabet.save()
        return test_extrabet

    def get_test_extrabet_api(self):
        test_extrabet = self.create_test_extrabet(self.test_user)
        return self.client.get('%s%i/' % (self.EXTRABETS_BASEURL, test_extrabet.pk))

    def create_test_extrabet_api(self):
        test_extra = ExtraApiTests.create_test_extra()
        return self.client.post(self.EXTRABETS_BASEURL, {'result_bet': 'Lyoner', 'extra': test_extra.pk}, format='json')

    def update_test_extrabet_api(self):
        test_extrabet = self.create_test_extrabet(self.test_user)
        test_extra = ExtraApiTests.create_test_extra()
        return self.client.put("%s%i/" % (self.EXTRABETS_BASEURL, test_extrabet.pk),
                               {'result_bet': 'Paprikasalami', 'extra': test_extra.pk}, format='json')

    def delete_test_extrabet_api(self):
        test_extrabet = self.create_test_extrabet(self.test_user)
        return self.client.delete("%s%i/" % (self.EXTRABETS_BASEURL, test_extrabet.pk))