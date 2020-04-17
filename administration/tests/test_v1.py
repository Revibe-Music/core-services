from django.db.utils import IntegrityError
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase, APIClient
from rest_framework.utils.serializer_helpers import ReturnList, ReturnDict
from oauth2_provider.models import Application

import datetime
import unittest

from revibe._errors import auth, permissions
from revibe._helpers import const
from revibe._helpers.test import RevibeTestCase
from revibe.utils.urls import add_query_params

from accounts.models import CustomUser, Profile
from administration.models import Alert, AlertSeen, Blog, ContactForm, YouTubeKey
from content.models import Artist, Album, Song

# -----------------------------------------------------------------------------

class TestContactForms(RevibeTestCase):
    def setUp(self):
        self._get_application()
        self._get_user()

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

        # send response
        response = self.client.post(url, data, format="json")

        # validate response
        self.assert400(response)


class TestCompanyViews(RevibeTestCase):
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
        self.assert403(broken)
    
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
        self.assert403(broken)

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
        self.assert403(broken)
    
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
        self.assert403(broken)

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
        self.assert403(broken, msg="Contact Form Metrics endpoint does not restrict to only Revibe staff")


class TestYoutubeKeyViews(RevibeTestCase):
    def setUp(self):
        self._get_application()
        self._get_user()
        self._get_youtube_key()
    
    def test_get_key(self):
        url = reverse('youtubekey-list')
        users = self.key.number_of_users

        # send the request
        response = self.client.get(url, format="json", **self._get_headers())

        # validate response
        self.assert200(response)
        self.assertTrue(
            'key' in response.data.keys(),
            msg="There is no 'key' field in the response"
        )

        updated_key = YouTubeKey.objects.get(**response.data)
        self.assertEqual(
            users+1, updated_key.number_of_users,
            msg="The number of users was not increased by one"
        )
    
    def test_send_bad_key_get_none(self):
        url = add_query_params(reverse('youtubekey-list'), {"old_key": str(self.key.key)})
        self.key.number_of_users = 1
        self.key.save()

        # send request
        response = self.client.get(url, format="json", **self._get_headers())

        # validate the response
        self.assert503(response)
        self.assertEqual(
            YouTubeKey.objects.get(key=str(self.key.key)).number_of_users, 0,
            msg="Number of users was not decreased by one"
        )


class TestAlertViews(RevibeTestCase):
    def setUp(self):
        self._get_application()
        self._get_user()
        self._get_alert()
    
    def test_get_alerts(self):
        # make sure there are alerts to see
        print("number of alerts", Alert.objects.all().count())
        self.assertTrue(
            Alert.objects.all().count() > 0,
            msg="There are no alerts to see"
        )

        # prep request
        url = reverse('alerts-list')

        # send request
        response = self.client.get(url, format="json", **self._get_headers())

        # validate response
        self.assert200(response)
        self.assertTrue(
            len(response.data['results']) > 0,
            msg="No alerts are recorded"
        )
    
    def test_see_alert(self):
        url = reverse('alerts-list')
        data = {
            "alert_id": str(self.alert.id)
        }

        # send request
        response = self.client.post(url, data=data, format="json", **self._get_headers())

        # validate response
        self.assert201(response)
        self.assertTrue(
            AlertSeen.objects.all().count() > 0,
            msg="The alert was not recorded as having been seen"
        )

    def test_get_alerts_seen_one(self):
        url = reverse('alerts-list')

        # pre-record seeing the alert
        AlertSeen.objects.create(alert=self.alert, user=self.user, has_seen=True)

        # send request
        response = self.client.get(url, format="json", **self._get_headers())

        # validate response
        self.assert200(response)
        self.assertTrue(
            response.data['results'] == [],
            msg="The alert still came up"
        )


class TestBlogViews(RevibeTestCase):
    def setUp(self):
        self._get_application()
        self._get_user()
        self._get_superuser()
        self._get_blog()

    def test_retrieve_posts(self):
        # configure test
        url = reverse('blog-list')

        # send request
        response = self.client.get(url, format="json")

        # send response
        self.assert200(response)
        self.assertEqual(
            str(response.data['results'][0]['id']), str(self.blog.id),
            msg="The correct blog was not returned"
        )

    def test_retrieve_single_post(self):
        # configure test
        url = reverse('blog-detail', args=[self.blog.id])

        # send request
        response = self.client.get(url, format="json")

        # validate response
        self.assert200(response)
        self.assertEqual(
            str(response.data['id']), str(self.blog.id),
            msg="The correct blog was not returned"
        )
    
    def test_retrieve_wrong_post(self):
        date = datetime.date.today() + datetime.timedelta(days=2)
        new_blog = Blog.objects.create(category="other", title="test2", body="test2", publish_date=date, author=self.superuser)

        # configure test
        url = reverse('blog-detail', args=[new_blog.id])

        # send request
        response = self.client.get(url, format="json")

        # validate response
        self.assert404(response)


