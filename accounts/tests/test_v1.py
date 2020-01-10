from django.urls import reverse
from rest_framework.test import APITestCase, APIClient
from rest_framework.utils.serializer_helpers import ReturnList, ReturnDict

import io
import os
from PIL import Image

import logging
logger = logging.getLogger(__name__)

from revibe._helpers.test import RevibeTestCase
from revibe._helpers import status

from accounts.models import CustomUser, Profile
from content.models import Artist

# -----------------------------------------------------------------------------

class TestRegister(RevibeTestCase):
    def setUp(self):
        self._get_application()

    def test_register(self):
        """
        Ensure we can create a new account object,
        and that those objects have unique usernames
        """
        url = reverse('register')
        data = {
            "username": "testing_username",
            "password": "testing_password",
            "device_type": "browser",
            "profile": {},
        }
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(CustomUser.objects.get(username=data['username']).username, data['username'])


class TestLogin(RevibeTestCase):
    def setUp(self):
        self._get_application()
        self._get_user()
        CustomUser.objects.create_user("login","login@login.com","password")

    def test_login(self):
        url = reverse('login')
        data = {
            "username": "login",
            "password": "password",
            "device_type": "browser",
        }
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['user']['username'], data['username'])
        assert 'access_token' in response.data.keys(), "No Access Token returned"
        assert 'refresh_token' not in response.data.keys(), "Refresh Token was returned"


class TestUserAccount(RevibeTestCase):
    def setUp(self):
        self._get_application()
        self._get_user()

    def test_get_profile(self):
        url = reverse('profile')
        response = self.client.get(url, **self._get_headers())
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        expected_fields = ['first_name','last_name','username','profile','is_artist','is_manager']
        expected_profile_fields = ['email','country','allow_explicit','allow_listening_data','allow_email_marketing']

        for field in expected_fields:
            assert field in response.data.keys(), "Expected {} in response fields".format(field)
        
        for profile_field in expected_profile_fields:
            assert profile_field in response.data['profile'].keys(), "Expected {} in response profile fields".format(profile_field)

    def test_edit_profile(self):
        url = reverse('profile')
        data = {"first_name": "John", "last_name": "Snow", "profile": {"country": "extremely cool country!"}}
        response = self.client.patch(url, data, format="json", **self._get_headers())

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['first_name'], "John")
        self.assertEqual(response.data['profile']['country'], 'extremely cool country!')

    def test_refresh_token(self):
        url = reverse('refresh-token')
        data = {
            "refresh_token": self.refresh_token,
            "device_type":"phone"
        }
        response = self.client.post(url, data, format="json", **self._get_headers())

        self.assert200(response.status_code)
        self.assertNotEqual(response.data['access_token'], self.access_token)

        # reset self's access token, in case the other requests come after
        if response.data['access_token'] != self.access_token:
            self.access_token = response.data['access_token']
    
    def test_refresh_token_bad(self):
        url = reverse('refresh-token')
        data = {
            "refresh_token": self.refresh_token,
        }
        response = self.client.post(url, data, format="json", **self._get_headers())

        self.assertEqual(response.status_code, status.HTTP_417_EXPECTATION_FAILED)


class TestArtistAccount(RevibeTestCase):
    def setUp(self):
        self._get_application()
        self._get_user()
        self._get_artist_user()

    def generate_artist_user(self):
        # create the user to become an artist
        user = CustomUser.objects.create_user("artist","artist@artist.com","artist")
        user_profile = Profile.objects.create(user=user)
        user.save()
        user_profile.save()

        url = reverse('login')
        data = {"username":"artist","password":"artist","device_type":"browser"}
        response = self.client.post(url, data, format="json")
        self.temp_user = user
        self.temp_access_token = response.data['access_token']

    def generate_artist_iamge(self):
        file = io.BytesIO()
        image = Image.new('RGBA', size=(100, 100), color=(155, 0, 0))
        image.save(file, 'png')
        file.name = 'test.png'
        file.seek(0)
        return file

    def test_register_artsit(self):
        self.generate_artist_user()
        # send the response
        url = reverse('artistaccount-list')
        data = {
            "name":"Test Register Artist",
            "image": self.generate_artist_iamge()
        }
        response = self.client.post(url, data, format="multipart", **self._get_headers(other=self.temp_access_token))

        # tests
        self.assert201(response.status_code)
        self.assertEqual(type(response.data), ReturnDict, msg="Response was not in the correct format")
        self.assertTrue('artist_profile' in response.data.keys(), msg="Response did not contain an 'Artist Profile' object")
        self.assertTrue('user' in response.data.keys(), msg="Response did not contain a 'User' object")
        self.assertTrue('profile' in response.data['user'].keys(), msg="Artist's 'User' object did contain a profile")

        created_artist = Artist.objects.get(id=response.data['artist_id'])
        self.assertEqual(self.temp_user, created_artist.artist_user)
        self.assertEqual(created_artist.artist_profile.require_contribution_approval, True, "Require contribution approval did not default correctly")
    
    def test_register_artist_user_already_has_artist(self):
        """
        Test if a user that already has an artist account can register a new
        artist.

        Should fail.
        """
        url = reverse('artistaccount-list')
        data = {
            "name":"Shouldn't work",
            "image":self.generate_artist_iamge()
        }
        response = self.client.post(url, data, format="multipart",**self._get_headers(artist=True))

        self.assert409(response)


    def test_edit_artist_profile(self):
        url = reverse('artistaccount-list')
        data = {
            "name":"Very New Name, Not The Same Name At All",
            "image":self.generate_artist_iamge()
        }
        response = self.client.patch(url, data, format="multipart", **self._get_headers(artist=True))

        self.assert200(response.status_code)
        self.assertEqual(type(response.data), ReturnDict)
        self.assertEqual(response.data['artist_id'], str(self.artist_user.artist.id))
        self.assertNotEqual(response.data['name'], self.artist_user.artist.name, "New name is the same as old name")
        # update self.artist_user
        new_artist = Artist.objects.get(id=response.data['artist_id'])
        self.artist_user = new_artist.artist_user

        self.assertEqual(
            new_artist.name, data['name'],
            msg="Database did not update with new name"
        )

    def test_get_artist_profile(self):
        url = reverse('artistaccount-list')
        response = self.client.get(url, format="json", **self._get_headers(artist=True))

        self.assert200(response, msg=_("Response code is not 200"))
        self.assertEqual(
            type(response.data), ReturnDict,
            msg="Response is not of the correct type"
        )
        self.assertTrue(
            'artist_profile' in response.data.keys(),
            msg="Returned artist does not contain an artist profile"
        )
        self.assertEqual(
            str(response.data['artist_id']), str(self.artist_user.artist.id),
            msg="The artist returned is not the authenticated artist"
        )

