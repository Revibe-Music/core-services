from django.test import TestCase
from rest_framework.test import APIRequestFactory,RequestsClient
from .views import *


class AuthenticationTest(TestCase):
    def setUp(self):
        self.base_url  = 'http://127.0.0.1:8000/accounts/'
        print("setting up...")

    def test_register(self):
        client = RequestsClient()
        # headers={"Content-Type": "application/x-www-form-urlencoded"}
        headers = {'Content-Type': 'application/json'}
        data = {
            "first_name": "test",
            "last_name": "test",
            "username": "test1",
            "password": "test1",
            "email": "test@gmail.com",
            "profile": {
                "country": "",
                "image": None
            }
        }
        response = client.post(self.base_url+'register/',data=json.dumps(data),headers=headers)
        print(response.json())
        self.assertEqual(response.status_code, 200)
