from django.urls import reverse
from rest_framework.utils.serializer_helpers import ReturnList, ReturnDict

from collections import OrderedDict

from logging import getLogger
logger = getLogger(__name__)

from revibe._helpers import const, status
from revibe._helpers.test import RevibeTestCase

from content.models import Album
from music.models import Library, Playlist

# -----------------------------------------------------------------------------


class TestLibrary(RevibeTestCase):
    def setUp(self):
        self._get_application()
        self._get_user()
        self._create_song()
    
    def test_list_libraries(self):
        url = reverse('library-list')
        response = self.client.get(url, format="json", **self._get_headers())

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(type(response.data), ReturnList)
        self.assertEqual(len(response.data), 2)
    
    def test_save_revibe_song(self):
        url = reverse('library-songs')
        data = {
            "platform": "Revibe",
            "song_id": self.content_song.id
        }
        response = self.client.post(url, data, format="json", **self._get_headers())

        self.assert201(response)
        self.assertReturnDict(response)
        self.assertEqual(
            response.data['song']['song_id'], str(self.content_song.id),
            msg="The returned song ID is not the sent song ID"
        )
        
        # check that the song is in fact in the user's library
        library = Library.objects.get(user=self.user, platform="Revibe")
        self.assertTrue(
            str(self.content_song.id) == str(library.songs.all()[0].id), # have to cast ID's as strings, the object ID's come back as UUIID and str, respectively
            msg="The song is not stored in the library"
        )

    def test_save_youtube_song(self):
        # send request
        url = reverse('library-songs')
        data = {
            "platform": 'youtube',
            "artist": {
                "artist_id": "456y2urj3kef",
                "artist_uri": "u7q3iaervo83thiger",
                "name": "YouTube Guy",
                "image_refs": [
                    {
                        "ref": "whatever.com/iwign.jpg",
                        "height": "450",
                        "width": "450",
                    }
                ]
            },
            "album": {
                "image_refs": [
                    {
                        "ref": "whatever.com/iwign.jpg",
                        "height": "300",
                        "width": "300",
                    }
                ]
            },
            "song": {
                "song_id": "2346790",
                "song_uri": "123467890",
                "title" : "The Guy's Song",
                "duration": "349",
            }
        }
        response = self.client.post(url, data, format="json", **self._get_headers())

        # validate response
        if response.status_code != 201:
            print(response.data)
        self.assert201(response)
        self.assertReturnDict(response)
        self.assertEqual(
            1, Album.objects.filter(song__id=data['song']['song_id']).count(),
            msg="Could not find an album with the correct song ID"
        )
        required_fields = ['library', 'song']
        for field in required_fields:
            self.assertTrue(
                field in response.data.keys(),
                msg=f"{field} not in response fields"
            )

    def test_save_spotify_song(self):
        """
        Creates a Spotify library for the user first
        """
        # create the spotify library
        lib = Library.objects.create(platform='Spotify', user=self.user)
        lib.save()

        # send request
        url = reverse('library-songs')
        data = {
            "platform":"spotify",
            "artist": {
                "artist_id": "28pwovyrh",
                "artist_uri":"918q3y9ptfrh",
                "name":"Spotify Boi",
                "image_ref": "83yetu.com/yaboi.png"
            },
            "album": {
                "album_id": "8tj89frjyegnufh8ui",
                "album_uri": "hygjou9ehtj",
                "name":"Dat Boi the Album",
                "image_ref": "jywefrtni.hua"
            },
            "song": {
                "song_id": "75ythjgvo9r48uyhrtjfio",
                "song_uri": "uhtjgkocdieu3hrjkfdox9",
                "title": "dat Boi's song",
                "duration": "430"
            }
        }
        response = self.client.post(url, data, format="json", **self._get_headers())

        # validate response
        if response.status_code != 201:
            print(response.data)
        self.assert201(response)

        # delete that library
        lib.delete()

    def test_save_spotify_song_no_library(self):
        """
        Save a spotify song when the user does not have a spotify library
        """
        # send request
        url = reverse('library-songs')
        data = {
            "platform":"spotify",
            "artist": {
                "artist_id": "28pwovyrh",
                "artist_uri":"918q3y9ptfrh",
                "name":"Spotify Boi",
                "image_ref": "83yetu.com/yaboi.png"
            },
            "album": {
                "album_id": "8tj89frjyegnufh8ui",
                "album_uri": "hygjou9ehtj",
                "name":"Dat Boi the Album",
                "image_ref": "jywefrtni.hua"
            },
            "song": {
                "song_id": "75ythjgvo9r48uyhrtjfio",
                "song_uri": "uhtjgkocdieu3hrjkfdox9",
                "title": "dat Boi's song",
                "duration": "430"
            }
        }
        response = self.client.post(url, data, format="json", **self._get_headers())

        # validate response
        self.assert400(response)

class TestPlaylists(RevibeTestCase):
    def setUp(self):
        self._get_application()
        self._get_user()
        self._create_song()

        self.added_songs = False
        self.created_playlist = False

    def test_playlist_list(self):
        url = reverse('playlist-list')

        response = self.client.get(url, format="json", **self._get_headers())
        self.assert200(response.status_code)

        results = response.data['results']
        self.assertEqual(type(results), ReturnList)
        self.assertEqual(len(results), len(Playlist.objects.filter(user=self.user)))
        if len(results) > 0:
            for playlist in results:
                self.assertEqual(str(self.user.id), str(playlist.user.id), msg="Returned a playlist that didn't belong to the current user")

    def test_create_playlist(self):
        url = reverse('playlist-list')
        name = "Test Creating a playlist"
        data = {
            "name": name
        }

        playlists_before = Playlist.objects.count()

        response = self.client.post(url, data, format="json", **self._get_headers())
        self.assert201(response.status_code)
        self.assertEqual(response.data['name'], name)
        self.assertEqual(Playlist.objects.count(), playlists_before+1)

        self.created_playlist = True
        self.playlist_id = response.data['id']
    
    def test_add_song(self):
        if not self.created_playlist:
            self.test_create_playlist()
        assert Playlist.objects.count() >= 1, "could not find any playlists to add to"
        playlist_id = Playlist.objects.all()[0].id
        playlist_songs_before = len(Playlist.objects.get(id=playlist_id).songs.all())

        url = reverse('playlist-songs')
        data = {
            "playlist_id": playlist_id,
            "song_id": self.content_song.id
        }

        response = self.client.post(url, data, format="json", **self._get_headers())
        self.assert201(response.status_code)
        self.assertEqual(playlist_songs_before + 1, len(Playlist.objects.get(id=playlist_id).songs.all()))

        self.added_songs = True
    
    def test_add_youtube_song(self):
        if not self.created_playlist:
            self.test_create_playlist()
        if not self.created_playlist:
            self.fail("Could not verify that a playlist was created")

        # send request
        url = reverse('playlist-songs')
        data = {
            "playlist_id": self.playlist_id,
            "platform": 'youtube',
            "artist": {
                "artist_id": "456y2urj3kef",
                "artist_uri": "u7q3iaervo83thiger",
                "name": "YouTube Guy",
                "image_refs": [{
                    "ref": "hello.com/hello.png",
                    "height": "10",
                    "width": "10"
                }]
            },
            "album": {
                "image_refs": [{
                    "ref": "9ui3wrsg.com/h3otgnerv.jpg",
                    "height": "10",
                    "width": "10"
                }]
            },
            "song": {
                "song_id": "2346790",
                "song_uri": "123467890",
                "title" : "The Guy's Song",
                "duration": "349",
            }
        }
        response = self.client.post(url, data, format="json", **self._get_headers())

        # validate response
        if response.status_code != 201:
            print(response.data)
        self.assert201(response)

    def test_delete_song(self):
        if not self.added_songs:
            self.test_add_song()
        assert Playlist.objects.count() >= 1, "could not find any playlists to delete songs from"
        playlist = Playlist.objects.filter(user=self.user)[0]
        assert len(playlist.songs.all()) > 0, "could not find any songs to delete"
        playlist_songs_before = len(playlist.songs.all())

        song_id = playlist.songs.all()[0].id

        url = reverse('playlist-songs')
        data = {
            "playlist_id": playlist.id,
            "song_id": song_id
        }

        response = self.client.delete(url, data, format="json", **self._get_headers())
        self.assert204(response.status_code)
        self.assertEqual(playlist_songs_before - 1, len(Playlist.objects.get(id=playlist.id).songs.all()))
    
    def test_add_multiple_songs(self):
        if not self.created_playlist:
            self.test_create_playlist()
        if not self.created_playlist:
            self.fail("Could not verify that a playlist was created")
        
        url = reverse('playlist-songs-bulk')
        data = {
            "playlist_id": self.playlist_id,
            "songs": [
                {
                    "platform": "spotify",
                    "artist": [
                        {
                            "artist_id": "21wesdfgyhui90",
                            "artist_uri": "pw8vy54tn",
                            "name": "Hello Boiiiiissss",
                            "image_refs": [{
                                "ref": "hello.com/hello.jpg",
                                "height": 1,
                                "width": 1
                            }]
                        },{
                            "artist_id": "qcin4yt",
                            "artist_uri": "cqw3mn498c",
                            "name": "Not You",
                            "image_refs": [{
                                "ref": "vwnieuro.com/qcv3ui4n",
                                "height": 10000,
                                "width": 10000
                            }]
                        }
                    ],
                    "album": {
                        "album_id": "q8n349tcyoyctqn",
                        "album_uri": "lni7w4fcdt4y3",
                        "name": "It's me again",
                        "image_refs": [{
                            "ref": "oiefiofe.aoi;fn/oaoiefg.ed",
                            "height": 2,
                            "width": 2
                        }]
                    },
                    "song": {
                        "song_id": "akerunf",
                        "song_uri": "ouoian",
                        "title": "Bois in the back",
                        "duration": "179",
                        "genre": "Indie-Folk"
                    }
                },{
                    "platform": "youtube",
                    "artist": {
                        "artist_id": "ajkv",
                        "artist_uri": "cqt3iun4",
                        "name": "Vivo Xi",
                        "image_refs": [{
                            "ref": "qcw4niuo4yiuchnet4w",
                            "height": 2,
                            "width": 2
                        }]
                    },
                    "album": {
                        "image_refs": [{
                            "ref": "qc4wu",
                            "height": 3,
                            "width": 3
                        }]
                    },
                    "song": {
                        "song_id": "awxf4f",
                        "song_uri": "ax3r22",
                        "title": "Ping my Pong",
                        "duration": "451"
                    }
                }
            ]
        }

        # send request
        response = self.client.post(url, data=data, format="json", **self._get_headers())

        # validate response
        print(response.data)
        self.assert201(response)
        self.assertReturnDict(response)


