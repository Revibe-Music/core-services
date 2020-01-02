from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase, APIClient
from rest_framework.utils.serializer_helpers import ReturnList, ReturnDict

from logging import getLogger
logger = getLogger(__name__)

from artist_portal._helpers.test import AuthorizedAPITestCase, AuthorizedContentAPITestCase
from content import models as cnt_models

# -----------------------------------------------------------------------------

class TestArtists(AuthorizedContentAPITestCase):
    def setUp(self):
        self._get_application()
        self._get_user()
        self._create_artist()

    def test_artist_list(self):
        url = reverse('artist-list')
        response = self.client.get(url, format="json", **self._get_headers())

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), cnt_models.Artist.objects.count())
        self.assertEqual(type(response.data), ReturnList)

class TestAlbums(AuthorizedContentAPITestCase):
    def setUp(self):
        self._get_application()
        self._get_user()
        self._create_album()
        self._create_song()
    
    def test_album_list(self):
        url = reverse('album-list')
        response = self.client.get(url, format="json", **self._get_headers())

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), cnt_models.Album.objects.count())
        self.assertEqual(type(response.data), ReturnList)

    def test_album_details(self):
        url = reverse('album-detail', args=[self.album.id])
        response = self.client.get(url, format="json", **self._get_headers())

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(type(response.data), ReturnDict)

    def test_album_songs(self):
        url = reverse('album-songs', args=[self.album.id])
        response = self.client.get(url, format="json", **self._get_headers())

        self.assert200(response.status_code)
        self.assertEqual(type(response.data), ReturnList)
        self.assertEqual(len(response.data), cnt_models.Album.objects.get(id=self.album.id).song_set.filter(is_displayed=True, is_deleted=False).count(), msg="Response data length is not all album songs")


