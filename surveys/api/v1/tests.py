"""
Created: 03 June 2020
Author: Jordan Prechac
"""

from django.urls import reverse

from revibe._helpers import status
from revibe._helpers.test import RevibeTestCase

from surveys.models import ArtistOfTheWeek

# -----------------------------------------------------------------------------

class ArtistOfTheWeekTestCase(RevibeTestCase):
    def setUp(self):
        self._get_application()
        self._get_user()
        self._get_artist_user()
        self._get_artistoftheweek()

    def test_post_application(self):
        url = reverse('artistoftheweek-application-list')
        data = {
            "promotion_ideas": "Shit could be so dope!",
        }

        # send the request
        response = self.client.post(url, data, format="json", **self._get_headers(artist=True))

        # validate the response
        self.assert201(response)

    def test_get_applications(self):
        url = reverse('artistoftheweek-application-list')

        # send the request
        response = self.client.get(url, format="json", **self._get_headers(artist=True))

        # validate the response
        self.assert200(response)
        self.assertReturnList(response)
    
    def test_get_application_detail(self):
        app = ArtistOfTheWeek.objects.filter(user=self.artist_user).first()
        url = reverse('artistoftheweek-application-detail', args=[app.id])

        # send the request
        response = self.client.get(url, format="json", **self._get_headers(artist=True))

        # validate the response
        self.assert200(response)
        self.assertReturnDict(response)

    def test_get_applications_not_artist(self):
        url = reverse('artistoftheweek-application-list')

        # send the request
        response = self.client.get(url, format="json", **self._get_headers())

        # validate the response
        self.assert403(response)



