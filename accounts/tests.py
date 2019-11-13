from django.test import TestCase
from rest_framework.test import APIRequestFactory,RequestsClient
from .views import *
from .models import *
from oauth2_provider.models import Application



class AuthenticationTest(TestCase):
    def setUp(self):
        self.base_url  = 'http://127.0.0.1:8000/accounts/'
        self.test_user = CustomUser.objects.create_user("test_user", "test@user.com", "123456")
        self.application = Application(
            name="Revibe First Party Application",
            redirect_uris="http://127.0.0.1:8000/",
            user=self.test_user,
            client_type=Application.CLIENT_CONFIDENTIAL,
            authorization_grant_type=Application.GRANT_PASSWORD,
        )
        self.application.save()

    def test_register(self):
        client = RequestsClient()
        headers = {'Content-Type': 'application/json'}
        data = {
            "first_name": "test",
            "last_name": "test",
            "username": "test12131",
            "password": "test11344",
            "email": "test1313@gmail.com",
            "profile": {
                "country": "",
                "image": None
            }
        }
        response = client.post(self.base_url+'register/',data=json.dumps(data),headers=headers)
        print(response.json())
        self.assertEqual(response.status_code, 200)
