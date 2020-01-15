from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase, APIClient
from rest_framework.utils.serializer_helpers import ReturnList, ReturnDict

from collections import OrderedDict

from logging import getLogger
logger = getLogger(__name__)

from revibe._helpers import const
from revibe._helpers.test import RevibeTestCase
from content import models as cnt_models

# -----------------------------------------------------------------------------

class TestArtists(RevibeTestCase):
    def setUp(self):
        self._get_application()
        self._get_user()
        self._create_artist()
        self._create_album()
        self._create_song()

    def test_artist_list(self):
        url = reverse('artist-list')
        response = self.client.get(url, format="json", **self._get_headers())

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), cnt_models.Artist.objects.filter(platform=const.REVIBE_STRING).count())
        self.assertEqual(type(response.data['results']), ReturnList)

        # pagination
        self.assertEqual(len(response.data), 4)
        self.assertEqual(type(response.data), OrderedDict)

    def test_artist_details(self):
        url = reverse('artist-detail', args=[self.content_artist.id])
        response = self.client.get(url, format="json", **self._get_headers())

        self.assert200(response.status_code)
        self.assertEqual(type(response.data), ReturnDict)
        self.assertEqual(str(response.data['artist_id']), str(self.content_artist.id))
    
    def test_artist_albums(self):
        url = reverse('artist-cnt-artist-albums', args=[self.content_artist.id])
        response = self.client.get(url, format="json", **self._get_headers())

        self.assert200(response.status_code)
        self.assertEqual(type(response.data['results']), ReturnList)
        self.assertEqual(len(response.data['results']), cnt_models.Album.objects.filter(uploaded_by=self.content_artist, is_displayed=True, is_deleted=False).count())

    def test_artist_songs(self):
        url = reverse('artist-cnt-artist-songs', args=[self.content_artist.id])
        response = self.client.get(url, format="json", **self._get_headers())

        self.assert200(response.status_code)
        self.assertEqual(type(response.data['results']), ReturnList, msg="Artist songs not returned in correct format")
        self.assertEqual(len(response.data['results']), cnt_models.Song.objects.filter(uploaded_by=self.content_artist, is_displayed=True, is_deleted=False).count(), msg="Artist songs not returning as much data as it should be")


class TestAlbums(RevibeTestCase):
    def setUp(self):
        self._get_application()
        self._get_user()
        self._create_album()
        self._create_song()
    
    def test_album_list(self):
        url = reverse('album-list')
        response = self.client.get(url, format="json", **self._get_headers())

        self.assert200(response)
        self.assertEqual(type(response.data), OrderedDict)
        self.assertEqual(len(response.data['results']), cnt_models.Album.objects.count())
        self.assertReturnList(response.data['results'])

    def test_album_details(self):
        url = reverse('album-detail', args=[self.content_album.id])
        response = self.client.get(url, format="json", **self._get_headers())

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(type(response.data), ReturnDict)

    def test_album_songs(self):
        url = reverse('album-songs', args=[self.content_album.id])
        response = self.client.get(url, format="json", **self._get_headers())

        self.assert200(response.status_code)
        self.assertEqual(type(response.data), ReturnList)
        self.assertEqual(len(response.data), cnt_models.Album.objects.get(id=self.content_album.id).song_set.filter(is_displayed=True, is_deleted=False).count(), msg="Response data length is not all album songs")


class TestSongs(RevibeTestCase):
    def setUp(self):
        self._get_application()
        self._get_user()
        self._create_song()
    
    def test_song_list(self):
        url = reverse('song-list')
        response = self.client.get(url, format="json", **self._get_headers())

        self.assert200(response.status_code)
        self.assertEqual(type(response.data), OrderedDict)
        self.assertTrue('results' in response.data.keys())
        self.assertReturnList(response.data['results'])


class TestSearch(RevibeTestCase):
    def setUp(self):
        self._get_application()
        self._get_user()
        self._create_song()
    
    def _get_url(self, **params):
        base = "/v1/content/search/"
        if params:
            start = True
            for key, value in params.items():
                connector = "?" if start else "&"
                base += f"{connector}{key}={value}"
                start = False
        return base

    def test_search(self):
        """
        Proper use of the search feature
        """
        url = self._get_url(**{"text":"Test"})

        response = self.client.get(url, format="json", **self._get_headers())
        self.assert200(response.status_code)
        self.assertEqual(type(response.data), dict)
        self.assertEqual(len(response.data.keys()), 3)
        for key, value in response.data.items():
            self.assertTrue(key in ['songs','albums','artists'], msg=f"{key} is not in response data keys")
            self.assertEqual(type(value), ReturnList)
        
    def test_search_with_selection(self):
        url = self._get_url(**{"text":"Test", "type":"songs"})

        response = self.client.get(url, format="json", **self._get_headers())
        self.assert200(response.status_code)
        self.assertEqual(type(response.data), dict)
        self.assertEqual(len(response.data), 1)
        for key, value in response.data.items():
            self.assertEqual(key, "songs")
            self.assertEqual(type(value), ReturnList)

    def test_search_no_text(self):
        url = self._get_url()

        response = self.client.get(url, format="json", **self._get_headers())
        self.assertEqual(response.status_code, status.HTTP_417_EXPECTATION_FAILED)

    def test_search_bad_selection(self):
        url = self._get_url(**{"text":"Test", "type":"UH_OH_SPAGHETTIO"})

        response = self.client.get(url, format="json", **self._get_headers())
        self.assertEqual(response.status_code, status.HTTP_417_EXPECTATION_FAILED)

