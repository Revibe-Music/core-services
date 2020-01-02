from django.db.utils import IntegrityError
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase, APIClient
from rest_framework.utils.serializer_helpers import ReturnList, ReturnDict
from oauth2_provider.models import Application

import unittest

import logging
logger = logging.getLogger(__name__)

from accounts.models import CustomUser, Profile
from administration.models import ContactForm
from artist_portal._helpers import const
from artist_portal._helpers.test import AuthorizedAPITestCase
from content.models import Artist, Album, Song

# -----------------------------------------------------------------------------

class TestContactForms(AuthorizedAPITestCase):
    def setUp(self):
        self._get_application()
        self._get_user()

    def _get_headers(self):
        return {"Authorization": "Bearer {}".format(self.access_token)}

    def test_submit_contact_form(self):
        url = reverse('forms-contact-form')
        data = {
            "subject": "Message Subject",
            "message": "Everything sucks!",
            "user_id": self.user.id
        }
        response = self.client.post(url, data, format="json", **self._get_headers())

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        expected_fields = ['subject','message','id','user','resolved','assigned_to']
        for field in expected_fields:
            assert field in response.data.keys(), "Expected {} in response fields".format(field)
        self.assertEqual(ContactForm.objects.count(), 1)


class TestCompanyViews(AuthorizedAPITestCase):
    help = "Tests the CompanyViewSet functions in the Administration namespace"

    def setUp(self):
        self._get_application()
        self._get_user()
        self._get_superuser()
    
    def test_user_data(self):
        url = reverse('company-user-metrics')

        # proper authentication
        response = self.client.get(url, format="json", **self._get_headers(sper=True))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(type(response.data), dict)
        self.assertEqual(type(response.data['User Count']), int)
        self.assertEqual(type(response.data['Users']), ReturnList)

        # improper authentication
        with self.assertRaises(PermissionError) as context:
            broken = self.client.get(url, format="json", **self._get_headers())
        self.assertTrue("You do not have access for this request type" in str(context.exception))
    
    def test_artist_data(self):
        url = reverse('company-artist-metrics')

        # proper authentication
        response = self.client.get(url, format="json", **self._get_headers(sper=True))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(type(response.data), dict)
        self.assertEqual(type(response.data['Artist Count']), int, msg="Did not return an Artist count as an integer")
        self.assertEqual(type(response.data['Artists']), ReturnList, msg="Did not return Artists in a serializer list format")
        self.assertEqual(len(response.data['Artists']), Artist.objects.filter(platform=const.REVIBE_STRING).count(), msg="Response data list does not contain all revibe artists")
        self.assertEqual(len(response.data['Artists']), response.data['Artist Count'], msg="Response data list length does not equal response count")

        # improper authentication
        with self.assertRaises(PermissionError) as context:
            broken = self.client.get(url, format="json", **self._get_headers())
        self.assertTrue("You do not have access for this request type" in str(context.exception))

    def test_album_data(self):
        url = reverse('company-album-metrics')
        
        # proper authentication
        response = self.client.get(url, format="json", **self._get_headers(sper=True))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(type(response.data), dict)
        self.assertEqual(type(response.data['Album Count']), int)
        self.assertEqual(type(response.data['Albums']), ReturnList)
        self.assertEqual(len(response.data['Albums']), Album.objects.filter(platform=const.REVIBE_STRING).count())

        # improper authentication
        with self.assertRaises(PermissionError) as context:
            broken = self.client.get(url, format="json", **self._get_headers())
        self.assertTrue("You do not have access for this request type" in str(context.exception))
    
    def test_song_data(self):
        url = reverse('company-song-metrics')

        # proper authentication
        response = self.client.get(url, format="json", **self._get_headers(sper=True))
        self.assert200(response.status_code)
        self.assertEqual(type(response.data), dict)
        self.assertEqual(type(response.data['Song Count']), int)
        self.assertEqual(type(response.data['Songs']), ReturnList)
        self.assertEqual(len(response.data['Songs']), Song.objects.filter(platform=const.REVIBE_STRING).count(), "Response data list does not contain all revibe songs")
        self.assertEqual(len(response.data['Songs']), response.data['Song Count'], msg="Response data length does not equal response song count")

        # improper authentication
        with self.assertRaises(PermissionError) as context:
            broken = self.client.get(url, format="json", **self._get_headers())
        self.assertTrue("You do not have access for this request type" in str(context.exception), msg="Song Metrics endpoint does not restrict to only Revibe staff")



