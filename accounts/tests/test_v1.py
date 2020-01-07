from django.urls import reverse
from rest_framework.test import APITestCase, APIClient
from oauth2_provider.models import Application

import logging
logger = logging.getLogger(__name__)

from revibe._helpers.test import RevibeTestCase
from revibe._helpers import status

from accounts.models import CustomUser, Profile

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


# class TestRegisterArtist(APITestCase):
#     def setUp(self):
#         create_application()
#         self.user, self.access_token = create_artist_test_user()
    
#     def _get_headers(self):
#         return {"Authorization": "Bearer {}".format(self.access_token)}

#     def test_register_artist(self):
#         url = reverse('user_artist')
#         data = {
#             'name': "Artist Test Register",
#             "image": None
#         }
#         response = self.client.post(url, data, format="json", **self._get_headers())

#         self.assertEqual(response.status_code, status.HTTP_201_CREATED)
