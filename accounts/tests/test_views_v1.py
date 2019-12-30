from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase, APIClient
from oauth2_provider.models import Application

import logging
logger = logging.getLogger(__name__)

from accounts.models import CustomUser

# -----------------------------------------------------------------------------

def create_application():
    try:
        Application.objects.create(client_type="confidential", authorization_grant_type="password", name="Revibe First Party Application")
    except:
        pass

def create_test_user():
    client = APIClient()
    try:
        user = CustomUser.objects.create_user(username="johnsnow", password="password")
        user.profile = Profile.objects.create(country="US")
    except:
        user = CustomUser.objects.get(username="johnsnow")
    login = client.post(reverse('login'), {"username": "johnsnow","password": "password","device_id": "1234567890","device_name": "Django Test Case","device_type": "browser",}, format="json")
    return user, login.data['access_token']

class TestRegister(APITestCase):
    def setUp(self):
        create_application()

    def test_register(self):
        """
        Ensure we can create a new account object,
        and that those objects have unique usernames
        """
        url = reverse('register')
        data = {
            "username": "testing_username",
            "password": "testing_password",
            "device_id": "1234567890",
            "device_type": "browser",
            "device_name": "Django Test Case",
            "profile": {},
        }
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(CustomUser.objects.count(), 1)
        self.assertEqual(CustomUser.objects.get(username=data['username']).username, data['username'])

class TestLogin(APITestCase):
    def setUp(self):
        create_application()
        self.user = CustomUser.objects.create_user(username="johndoe", password="password")

    def test_login(self):
        url = reverse('login')
        data = {
            "username": "johndoe",
            "password": "password",
            "device_id": "1234567890",
            "device_name": "Django Test Case",
            "device_type": "browser",
        }
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['user']['username'], "johndoe")
        assert 'access_token' in response.data.keys(), "No Access Token returned"
        assert 'refresh_token' not in response.data.keys(), "Refresh Token was returned"


class TestUserAccount(APITestCase):
    def setUp(self):
        create_application()
        self.user, self.access_token = create_test_user()
        self.headers = {"Authorization": "Bearer {}".format(self.access_token)}
    
    def test_get_profile(self):
        url = reverse('profile')
        response = self.client.get(url, **self.headers)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_edit_profile(self):
        url = reverse('profile')
        data = {"first_name": "John", "last_name": "Snow"}
        response = self.client.patch(url, data, format="json", **self.headers)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['first_name'], "John")

