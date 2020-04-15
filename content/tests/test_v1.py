from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase, APIClient
from rest_framework.utils.serializer_helpers import ReturnList, ReturnDict

from collections import OrderedDict

from logging import getLogger
logger = getLogger(__name__)

from revibe._helpers import const
from revibe._helpers.test import RevibeTestCase
from revibe.utils.urls import add_query_params

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
        return add_query_params(base, params)

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


class TestBrowse(RevibeTestCase):
    def setUp(self):
        self._get_application()
        self._get_user()
        self._create_song()

        self.base_url = "/v1/content/browse/"
        self.songs_type = "songs"
        self.albums_type = "albums"
        self.artist_type = "artists"

    def _get_url(self, base="/v1/content/browse/", **params):
        return add_query_params(base, params)

    def test_browse_page(self):
        """
        Basic test to make sure anything is returned and in the proper format
        """
        url = self._get_url()

        # send request
        response = self.client.get(url, format="json", **self._get_headers())

        # validate response
        self.assert200(response.status_code)
        self.assertReturnList(response, msg="Response is not the correct type")
    
    # Browse Sections
    def _section_tster(self, endpoint, type_, *args, **kwargs):
        """
        utility function for testing all endpoints
        """
        url = self._get_url(base=self.base_url+endpoint+"/")

        # send request
        response = self.client.get(url, format="json", **self._get_headers())

        # configure validation
        return_type = kwargs.pop('return_type', 'return_dict')

        # validate response
        self.assert200(response)

        if return_type == 'return_dict':
            self.assertReturnDict(response)
        elif return_type == 'return_list':
            self.assertReturnList(response)

        self.assertEqual(
            response.data['type'], type_,
            msg=f"Response 'type' is not {type_}"
        )
        self.assertTrue(
            response.data['endpoint'] in url,
            msg=f"The returned 'endpoint' value {response.data['endpoint']} is not within the request url {url}"
        )


    def test_all_sections(self):
        # self._section_tster("top-songs-all-time", self.songs_type)

        sections = [
            {
                "endpoint": "top-songs-all-time",
                "type": self.songs_type
            },{
                "endpoint": "top-albums-all-time",
                "type": self.albums_type
            }, {
                "endpoint": "top-artists-all-time",
                "type": self.artist_type
            }, {
                "endpoint": "trending-songs",
                "type": self.songs_type
            }, {
                "endpoint": "trending-albums",
                "type": self.albums_type
            }, {
                "endpoint": "trending-artists",
                "type": self.artist_type
            },{
                "endpoint": "trending-youtube",
                "type": self.songs_type
            },{
                "endpoint": "recently-uploaded-albums",
                "type": self.albums_type
            },{
                "endpoint": "artist-spotlight",
                "type": "artist",
                "return_type": "return_dict"
            },{
                "endpoint": "revibe-playlists",
                "type": "playlists"
            }
        ]

        for sec in sections:
            self._section_tster(endpoint=sec.pop('endpoint'), type_=sec.pop('type'), **sec)



