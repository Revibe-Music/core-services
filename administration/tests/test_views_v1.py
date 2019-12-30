from django.db.utils import IntegrityError
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase, APIClient
from oauth2_provider.models import Application

import logging
logger = logging.getLogger(__name__)

from accounts.models import CustomUser, Profile
from administration.models import ContactForm

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
        profile = Profile.objects.create(country="US", user=user)
        profile.save()
        user.save()
    except IntegrityError as ie:
        user = CustomUser.objects.get(username="johnsnow")
    except Exception as e:
        raise(e)
    login = client.post(reverse('login'), {"username": "johnsnow","password": "password","device_id": "1234567890","device_name": "Django Test Case","device_type": "phone",}, format="json")
    return user, login.data['access_token'], login.data['refresh_token']

def create_test_superuser():
    client = APIClient()
    try:
        user = CustomUser.objects.create_superuser(username="admin", password="admin")
        profile = Profile.objects.create(country="US", user=user)
        profile.save()
        user.save()
    except IntegrityError as ie:
        user = CustomUser.objects.get(username="admin")
    except Exception as e:
        raise(e)
    login = client.post(reverse('login'), {"username": "admin","password": "admin","device_id": "1234567890admin","device_name": "Django Test Case","device_type": "phone",}, format="json")
    return user, login.data['access_token'], login.data['refresh_token']

# -----------------------------------------------------------------------------

class TestContactForms(APITestCase):
    def setUp(self):
        create_application()
        self.user, self.access_token, self.refresh_token = create_test_user()

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

