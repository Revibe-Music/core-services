from django.db.utils import IntegrityError
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase, APIClient
from rest_framework.utils.serializer_helpers import ReturnList, ReturnDict
from oauth2_provider.models import Application

import unittest

import logging
logger = logging.getLogger(__name__)

from revibe._errors import auth, permissions
from revibe._helpers import const
from revibe._helpers.test import AuthorizedAPITestCase

from accounts.models import CustomUser, Profile
from administration.models import ContactForm
from content.models import Artist, Album, Song

# -----------------------------------------------------------------------------

class TestContactForms(AuthorizedAPITestCase):
    def setUp(self):
        self._get_application()
        self._get_user()

    def _get_headers(self):
        return {"Authorization": "Bearer {}".format(self.access_token)}

    def test_submit_contact_form_user_id(self):
        url = reverse('forms-contact-form')
        data = {
            "subject": "Message Subject",
            "message": "Everything sucks!",
            "user_id": self.user.id
        }
        response = self.client.post(url, data, format="json", **self._get_headers())

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        expected_fields = ['subject','message','id','resolved','assigned_to']
        for field in expected_fields:
            assert field in response.data.keys(), "Expected {} in response fields".format(field)
        self.assertEqual(ContactForm.objects.count(), 1)
    
    def test_submit_contact_form_name_email(self):
        url = reverse('forms-contact-form')
        data = {
            "subject":"Issue",
            "message":"Make this shit work, fam!",
            "first_name":"John",
            "last_name":"Doe",
            "email":"john@doe.com",
        }
        response = self.client.post(url, data, format="json", **self._get_headers())

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        expected_fields = ['subject','message','id','resolved','assigned_to']
        for field in expected_fields:
            self.assertTrue(field in response.data.keys(), msg="Expected {} in response fields.".format(field))
    
    def test_submit_contact_form_auth(self):
        url = reverse('forms-contact-form')
        data = {
            "subject":"Uh oh",
            "message":"This won't work"
        }
        response = self.client.post(url, data, format="json", **self._get_headers())

        self.assert201(response.status_code)
    
    def test_submit_contact_form_fali(self):
        url = reverse('forms-contact-form')
        data = {
            "subject":"Uh oh",
            "message":"This won't work"
        }
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_417_EXPECTATION_FAILED)


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
        broken = self.client.get(url, format="json", **self._get_headers())
        self.assertEqual(broken.status_code, status.HTTP_417_EXPECTATION_FAILED)
    
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
        broken = self.client.get(url, format="json", **self._get_headers())
        self.assertEqual(broken.status_code, status.HTTP_417_EXPECTATION_FAILED)

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
        broken = self.client.get(url, format="json", **self._get_headers())
        self.assertEqual(broken.status_code, status.HTTP_417_EXPECTATION_FAILED)
    
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
        broken = self.client.get(url, format="json", **self._get_headers())
        self.assertEqual(broken.status_code, status.HTTP_417_EXPECTATION_FAILED)

    def test_contact_form_data(self):
        url = reverse('company-contact-form-metrics')

        response = self.client.get(url, format="json", **self._get_headers(sper=True))
        self.assert200(response.status_code)
        self.assertEqual(type(response.data), dict)
        self.assertEqual(type(response.data['Contact Form Count']), int)
        self.assertEqual(type(response.data['Contact Forms']), ReturnList)
        self.assertEqual(len(response.data['Contact Forms']), ContactForm.objects.count(), msg="Response does not contain all contact forms")
        self.assertEqual(len(response.data['Contact Forms']), response.data['Contact Form Count'], msg="Response data length does not equal response count")

        broken = self.client.get(url, format="json", **self._get_headers())
        self.assertEqual(broken.status_code, status.HTTP_417_EXPECTATION_FAILED, msg="Contact Form Metrics endpoint does not restrict to only Revibe staff")

