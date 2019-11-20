from django.test import TestCase
from rest_framework.test import APIRequestFactory,RequestsClient
from .views import *
from .models import *
from oauth2_provider.models import Application



class AuthenticationTest(TestCase):
    access_token = None
    refresh_token = None

    def setUp(self):
        self.base_url  = 'http://127.0.0.1:8000/account/'
        self.test_user = CustomUser.objects.create_user("test_user", "test@user.com", "123456")
        self.application = Application(
            name="Revibe First Party Application",
            redirect_uris="http://127.0.0.1:8000/",
            user=self.test_user,
            client_type=Application.CLIENT_CONFIDENTIAL,
            authorization_grant_type=Application.GRANT_PASSWORD,
        )
        self.application.save()


    def Test_register(self):
        client = RequestsClient()
        headers = {'Content-Type': 'application/json'}
        data = {
            "first_name": "test",
            "last_name": "test",
            "username": "test121312",
            "password": "test",
            "email": "test12313@gmail.com",
            "profile": {
                "country": "",
                "image": None
            }
        }
        response = client.post(self.base_url+'register/',data=json.dumps(data),headers=headers)
        self.assertEqual(response.status_code, 200)
        print("Register user test passed")

    def Test_login(self):
        client = RequestsClient()
        headers = {'Content-Type': 'application/json'}
        data = {"username": "test_user", "password": "123456"}
        response = client.post(self.base_url+'login/',data=json.dumps(data),headers=headers)
        token_data = response.json()
        self.__class__.access_token = token_data["token"]["access_token"]
        self.__class__.refresh_token = token_data["token"]["refresh_token"]
        self.assertEqual(response.status_code, 200)
        print("Login user test passed")

    def Test_refresh_token(self):
        client = RequestsClient()
        headers = {'Content-Type': 'application/json'}
        data = {"refresh_token": self.__class__.refresh_token}
        response = client.post(self.base_url+'token/refresh/',data=json.dumps(data),headers=headers)
        token_data = response.json()
        self.__class__.access_token = token_data["access_token"]
        self.__class__.refresh_token = token_data["refresh_token"]
        self.assertEqual(response.status_code, 200)
        print("Refresh Token test passed")

    def Test_logout(self):
        client = RequestsClient()
        headers = {'Content-Type': 'application/json', 'Authorization': 'Bearer '+self.__class__.access_token}
        data = {'access_token': self.__class__.access_token}
        response = client.post(self.base_url+'logout/',data=json.dumps(data),headers=headers)
        self.assertEqual(response.status_code, 200)
        print("Logout user test passed")

    def Test_logout_all(self):
        client = RequestsClient()
        headers = {'Content-Type': 'application/json', 'Authorization': 'Bearer '+self.__class__.access_token}
        response = client.post(self.base_url+'logout-all/',headers=headers)
        self.assertEqual(response.status_code, 200)
        print("Logout user test passed")

    def test_methods(self):
        self.Test_register()
        self.Test_login()
        self.Test_refresh_token()
        self.Test_logout()
        self.Test_login()
        self.Test_login()
        self.Test_logout_all()
