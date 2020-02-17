from django.urls import reverse
from rest_framework.test import APITestCase, APIClient
from rest_framework.utils.serializer_helpers import ReturnList, ReturnDict

import io
import os
from PIL import Image

import logging
logger = logging.getLogger(__name__)

from revibe._helpers.test import RevibeTestCase
from revibe._helpers import status

from accounts.models import CustomUser, Profile
from administration.models import Campaign
from content.models import *

# -----------------------------------------------------------------------------

class TestRegister(RevibeTestCase):
    def setUp(self):
        self._get_application()

    def test_register(self):
        """
        Ensure we can create a new account object,
        and that those objects have unique usernames
        """
        url = reverse('register')
        data = {
            "username": "testing_username",
            "password": "testing_password",
            "device_type": "browser",
            "profile": {},
        }
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(CustomUser.objects.get(username=data['username']).username, data['username'])
    
    def test_register_with_referral(self):
        """
        tests the registration feature with a referrer ID included
        """
        self._get_user()
        # send request
        url = str(reverse('register')) + f"?uid={self.user.id}"
        data = {
            "username": "anothertestusername",
            "password": "password",
            "device_type": "browser",
            "profile": {},
        }

        # validate response
        response = self.client.post(url, data, format="json")
        self.assert200(response)

        referrer = self.user
        new_user = CustomUser.objects.get(username=response.data['user']['username'])
        self.assertTrue(
            bool(getattr(new_user.profile, "referrer", False)),
            msg="Could not find the profile's 'referrer'"
        )
        self.assertEqual(
            str(referrer.id), str(new_user.profile.referrer.id),
            msg="The expected referrer is not listed as the new user's referrer"
        )

    def test_register_with_campaign(self):
        self._get_campaign()
        # send request
        url = str(reverse('register')) + f"?cid={self.campaign.uri}"
        data = {
            "username": "ipugawvjln",
            "password": "password",
            "device_type": "browser",
            "profile": {},
        }

        # validate response
        response = self.client.post(url, data, format="json")
        self.assert200(response)

        campaign = Campaign.objects.get(name='example campaign')
        new_user = CustomUser.objects.get(username=response.data['user']['username'])
        self.assertTrue(
            bool(getattr(new_user.profile, 'campaign', False)),
            msg="Could not find the profile's campaign"
        )
        self.assertEqual(
            str(campaign.id), str(new_user.profile.campaign.id),
            msg="The expected campaign is not listed as the user's campaign"
        )


class TestLogin(RevibeTestCase):
    def setUp(self):
        self._get_application()
        self._get_user()
        CustomUser.objects.create_user("login","login@login.com","password")

    def test_login(self):
        url = reverse('login')
        data = {
            "username": "login",
            "password": "password",
            "device_type": "browser",
        }
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['user']['username'], data['username'])
        assert 'access_token' in response.data.keys(), "No Access Token returned"
        assert 'refresh_token' not in response.data.keys(), "Refresh Token was returned"


class TestUserAccount(RevibeTestCase):
    def setUp(self):
        self._get_application()
        self._get_user()

    def test_get_profile(self):
        url = reverse('profile')
        response = self.client.get(url, **self._get_headers())
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        expected_fields = ['first_name','last_name','username','profile','is_artist','is_manager']
        expected_profile_fields = ['email','country','allow_explicit','allow_listening_data','allow_email_marketing']

        for field in expected_fields:
            assert field in response.data.keys(), "Expected {} in response fields".format(field)
        
        for profile_field in expected_profile_fields:
            assert profile_field in response.data['profile'].keys(), "Expected {} in response profile fields".format(profile_field)

    def test_edit_profile(self):
        url = reverse('profile')
        data = {"first_name": "John", "last_name": "Snow", "profile": {"country": "extremely cool country!"}}
        response = self.client.patch(url, data, format="json", **self._get_headers())

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['first_name'], "John")
        self.assertEqual(response.data['profile']['country'], 'extremely cool country!')

    def test_refresh_token(self):
        url = reverse('refresh-token')
        data = {
            "refresh_token": self.refresh_token,
            "device_type":"phone"
        }
        response = self.client.post(url, data, format="json", **self._get_headers())

        self.assert200(response.status_code)
        self.assertNotEqual(response.data['access_token'], self.access_token)

        # reset self's access token, in case the other requests come after
        if response.data['access_token'] != self.access_token:
            self.access_token = response.data['access_token']
    
    def test_refresh_token_bad(self):
        url = reverse('refresh-token')
        data = {
            "refresh_token": self.refresh_token,
        }
        response = self.client.post(url, data, format="json", **self._get_headers())

        self.assertEqual(response.status_code, status.HTTP_417_EXPECTATION_FAILED)


class TestArtistAccount(RevibeTestCase):
    def setUp(self):
        self._get_application()
        self._get_user()
        self._get_artist_user()

    def generate_artist_user(self):
        # create the user to become an artist
        user = CustomUser.objects.create_user("artist","artist@artist.com","artist")
        user_profile = Profile.objects.create(user=user)
        user.save()
        user_profile.save()

        url = reverse('login')
        data = {"username":"artist","password":"artist","device_type":"browser"}
        response = self.client.post(url, data, format="json")
        self.temp_user = user
        self.temp_access_token = response.data['access_token']

    def test_register_artsit(self):
        self.generate_artist_user()
        # send the response
        url = reverse('artistaccount-list')
        data = {
            "name":"Test Register Artist",
            "image": self.generate_image()
        }
        response = self.client.post(url, data, format="multipart", **self._get_headers(other=self.temp_access_token))

        # tests
        self.assert201(response.status_code)
        self.assertEqual(type(response.data), ReturnDict, msg="Response was not in the correct format")
        self.assertTrue('artist_profile' in response.data.keys(), msg="Response did not contain an 'Artist Profile' object")
        self.assertTrue('user' in response.data.keys(), msg="Response did not contain a 'User' object")
        self.assertTrue('profile' in response.data['user'].keys(), msg="Artist's 'User' object did contain a profile")

        created_artist = Artist.objects.get(id=response.data['artist_id'])
        self.assertEqual(self.temp_user, created_artist.artist_user)
        self.assertEqual(created_artist.artist_profile.require_contribution_approval, True, "Require contribution approval did not default correctly")
    
    def test_register_artist_user_already_has_artist(self):
        """
        Test if a user that already has an artist account can register a new
        artist.

        Should fail.
        """
        url = reverse('artistaccount-list')
        data = {
            "name":"Shouldn't work",
            "image":self.generate_image()
        }
        response = self.client.post(url, data, format="multipart",**self._get_headers(artist=True))

        self.assert409(response)

    def test_edit_artist_profile(self):
        url = reverse('artistaccount-list')
        data = {
            "name":"Very New Name, Not The Same Name At All",
            "image":self.generate_image()
        }
        response = self.client.patch(url, data, format="multipart", **self._get_headers(artist=True))

        self.assert200(response.status_code)
        self.assertEqual(
            type(response.data), ReturnDict,
            msg="Response is not in the correct format"
        )
        self.assertEqual(
            response.data['artist_id'], str(self.artist_user.artist.id),
            msg="Updated artist is not the authenticated artist"
        )
        self.assertNotEqual(
            response.data['name'], self.artist_user.artist.name,
            msg="New name is the same as old name"
        )

        # update self.artist_user
        new_artist = Artist.objects.get(id=response.data['artist_id'])
        self.artist_user = new_artist.artist_user

        self.assertEqual(
            new_artist.name, data['name'],
            msg="Database did not update with new name"
        )

    def test_get_artist_profile(self):
        url = reverse('artistaccount-list')
        response = self.client.get(url, format="json", **self._get_headers(artist=True))

        self.assert200(response)
        self.assertEqual(
            type(response.data), ReturnDict,
            msg="Response is not of the correct type"
        )
        self.assertTrue(
            'artist_profile' in response.data.keys(),
            msg="Returned artist does not contain an artist profile"
        )
        self.assertEqual(
            str(response.data['artist_id']), str(self.artist_user.artist.id),
            msg="The artist returned is not the authenticated artist"
        )


class TestArtistAlbums(RevibeTestCase):
    def setUp(self):
        self._get_application()
        self._get_user()
        self._get_artist_user()
        self._create_song()
        self.url = reverse('artistaccount-albums')

        # state variables
        self.uploaded = False
        self.edited = False

    def test_upload_album(self):
        data = {
            "name": "The Test Album",
            "image": self.generate_image(),
            "type":"Album",
        }
        response = self.client.post(self.url, data, format="multipart", **self._get_headers(artist=True))

        self.assert201(response)
        self.assertReturnDict(response)
        self.assertTrue(
            'contributors' in response.data.keys(),
            msg="response did not contain a 'contributors' list"
        )
        self.assertEqual(
            len(response.data['contributors']), 1,
            msg="'contributors' list did not contain the correct number of objects"
        )
        self.assertEqual(
            response.data['uploaded_by']['artist_id'], str(self.artist_user.artist.id),
            msg="Current artist is not the album's uploading artist"
        )
        self.assertEqual(
            response.data['uploaded_by']['artist_id'], response.data['contributors'][0]['artist_id'],
            msg="Uploading artist ID is not the contributor's artist ID"
        )

        # set state variables
        self.uploaded = True
        self.album_id = response.data['album_id']

    def test_upload_album_not_artist(self):
        data = {
            "Name":"Not gonna matter",
            "image":self.generate_image(),
            "type":"nonexistent"
        }
        response = self.client.post(self.url, data, format="multipart", **self._get_headers())

        # validate response
        self.assert403(response)

    def test_get_albums(self):
        response = self.client.get(self.url, format="json", **self._get_headers(artist=True))

        self.assert200(response)
        self.assertReturnList(response)
        for album in response.data:
            self.assertEqual(
                album['uploaded_by']['artist_id'], str(self.artist_user.artist.id),
                msg="Not all returned albums were uploaded by the current artist"
            )

    def test_edit_album(self):
        # validate album was uploaded
        if not self.uploaded:
            self.test_upload_album()
        if not self.uploaded:
            self.fail(msg="'test_upload_album' failed, cannot edit an album")

        # send request
        data = {
            "album_id": self.album_id,
            "name":"Much better name now"
        }
        response = self.client.patch(self.url, data, format="multipart", **self._get_headers(artist=True))

        # validate response
        self.assert200(response)
        self.assertReturnDict(response)
        self.assertEqual(
            response.data['album_id'], self.album_id,
            msg="Returned album is not the one that was sent (ID check)"
        )

        # check that all sent fields updated in db
        album = Album.objects.get(id=response.data['album_id'])
        for key, value in data.items():
            if not key == 'album_id':
                self.assertEqual(
                    value, getattr(album, key),
                    msg=f"{key} did not update correctly in database"
                )

        # update state variables
        self.edited = True

    def test_delete_album(self):
        # validate that album has been edited
        if not self.edited:
            self.test_edit_album()
        if not self.edited:
            self.fail("could not verify that album has been edited, cannot delete")
        
        # send response
        data = {
            "album_id": self.album_id,
        }
        response = self.client.delete(self.url, data, format="json", **self._get_headers(artist=True))

        # validate response
        self.assert204(response)

        self.assertTrue(
            Album.objects.get(id=self.album_id).is_deleted,
            msg="Did not set album 'is_deleted' to True"
        )
        for song in Album.objects.get(id=self.album_id).song_set.all():
            self.assertTrue(
                song.is_deleted,
                msg=f"Album song '{song}.is_deleted' was not set to True"
            )
        self.assertEqual(
            0, Album.display_objects.filter(id=self.album_id).count(),
            msg="The album is still showing up in 'display_objects'"
        )
        self.assertEqual(
            0, Song.display_objects.filter(album__id=self.album_id).count(),
            msg="The album's songs are still showing up in 'display_objects'"
        )


class TestArtistSongs(RevibeTestCase):
    def setUp(self):
        self._get_application()
        self._get_user()
        self._get_artist_user()
        self._get_second_artist_user()
        self._create_album()
        self.url = reverse('artistaccount-songs')
        album = Album.objects.create(name="The Best Album", uploaded_by=self.artist_user.artist)
        album.save()
        self.song_album = album

        # state variables
        self.song_uploaded = False
        self.song_edited = False

    def test_upload_song(self):
        """
        Upload a song from the current artist
        """
        data = {
            "title": "New Song!",
            "file":self.generate_image(),
            "duration":"180",
            "genre":"Country",
            "album_id":str(self.song_album.id)
        }
        response = self.client.post(self.url, data, format="multipart", **self._get_headers(artist=True))

        # validate response
        self.assert201(response)
        self.assertReturnDict(response)
        self.assertEqual(
            response.data['album']['album_id'], str(self.song_album.id),
            msg="Returned album id is not the sent album id"
        )
        song = Song.objects.get(id=response.data['song_id'])
        self.assertEqual(
            song.is_deleted, False,
            msg="The uploaded song was deleted by default"
        )

        # update state variables
        self.song_uploaded = True
        self.song_id = response.data['song_id']
    
    def test_upload_song_not_artist(self):
        """
        Test uploading a song when the user is not an artist

        Should fail
        """
        data = {
            "title":"not gonna upload",
            "file":self.generate_image(),
            "duration":"200",
            "album_id":str(self.song_album.id)
        }
        response = self.client.post(self.url, data, format="multipart", **self._get_headers())

        # validate response
        self.assert403(response)

    def test_upload_song_not_authenticated(self):
        """
        Upload a song when the request is not authenticated.

        Should fail
        """
        data = {
            "title":"not gonna work again",
            "file":self.generate_image(),
            "duration":"310",
            "album_id":str(self.song_album.id)
        }
        response = self.client.post(self.url, data, format="multipart")

        # validate response
        self.assert401(response)

    def test_edit_song(self):
        """
        Edit a song that has been uploaded
        """
        # pre-request validations
        if not self.song_uploaded == True:
            self.test_upload_song()
        if not self.song_uploaded == True:
            self.fail("Could not verify that a song was uploaded, cannot edit a non-existent song")
        old_title = Song.objects.get(id=self.song_id).title
        
        # send request
        data = {
            "song_id": self.song_id,
            "title":"New Title!"
        }
        response = self.client.patch(self.url, data, format="multipart", **self._get_headers(artist=True))

        # validate response
        self.assert200(response)
        self.assertReturnDict(response)
        self.assertEqual(
            response.data['song_id'], self.song_id,
            msg="Returned song is not the song that was uploaded"
        )
        self.assertEqual(
            response.data['title'], data['title'],
            msg="Returned title is not the same as the sent title"
        )
        self.assertEqual(
            response.data['title'], Song.objects.get(id=self.song_id).title,
            msg="Sent data was not saved to the database"
        )
        if 'title' in data.keys():
            self.assertNotEqual(
                old_title, response.data['title'],
                msg="Old title is the same as the new title"
            )

        # update state variables
        self.song_edited = True

    def test_edit_song_not_artist(self):
        """
        Test editing a song when not logged in as an artist
        """
        # pre-request validation
        if not self.song_uploaded:
            self.test_upload_song()
        if not self.song_uploaded:
            self.fail("could not validate that a song was uploaded")
        # send request
        data = {
            "song_id": self.song_id,
            "title":"Not an artist"
        }
        response = self.client.patch(self.url, data, format="multipart", **self._get_headers())

        # validate request
        self.assert403(response)

    def test_edit_song_not_uploader(self):
        """
        Edit a song that was not uploaded by the person editing the song
        """
        # check state
        if not self.song_uploaded:
            self.test_upload_song()
        if not self.song_uploaded:
            self.fail("Could not validate that a song was uploaded")
        
        # send request
        data = {
            "song_id": self.song_id,
            "title": "Not Gonna Work"
        }
        response = self.client.patch(self.url, data, format="json", **self._get_headers(artist2=True))

        # validate response
        self.assert403(response)

    def test_get_songs(self):
        # validate pre-request requirements
        if not self.song_uploaded == True:
            self.test_upload_song()
        if not self.song_uploaded == True:
            self.fail("Could not verify that a song was uploaded")
        
        # send request
        response = self.client.get(self.url, format="json", **self._get_headers(artist=True))

        # validate request
        self.assert200(response)
        self.assertReturnList(response)

        artist = Artist.objects.get(id=response.data[0]['uploaded_by']['artist_id'])
        self.assertEqual(
            len(response.data), Song.hidden_objects.filter(uploaded_by=artist).count(),
            msg="Did not return all of the artist's songs"
        )

    def test_delete_song(self):
        """
        Delete a song that this artist did upload
        """
        # pre-request validation
        if not self.song_edited:
            self.test_edit_song()
        if not self.song_edited:
            self.fail("Could not validate that the song had yet been edited")
        
        # send request
        data = {
            "song_id": self.song_id
        }
        response = self.client.delete(self.url, data, format="json", **self._get_headers(artist=True))

        # vaidate response
        self.assert204(response)
        self.assertEqual(
            0, Song.display_objects.filter(id=self.song_id).count(),
            msg="The song still appears in the 'display_objects' manager"
        )

    def test_delete_song_not_uploader(self): # can't test, don't have second artist account set up
        """
        Delete a song when not the one who uploaded that song
        Expect a 403
        """
        # check state
        if not self.song_uploaded:
            self.test_upload_song()
        if not self.song_uploaded:
            self.fail("Could not validate that a song was uploaded")

        # send request
        data = {
            "song_id": self.song_id
        }
        response = self.client.delete(self.url, data, format="json", **self._get_headers(artist2=True))

        # validate response
        self.assert403(response)


class TestArtistAlbumContribution(RevibeTestCase):
    def setUp(self):
        self._get_application()
        self._get_user()
        self._get_artist_user()
        self._get_second_artist_user()
        self._create_song()
        self.url = reverse('artistaccount-album_contributions')

        _album = Album.objects.create(name="917834520", uploaded_by=self.artist, platform="Revibe")
        _album.save()
        self.album_id = _album.id

        # state variables
        self.contrib_added = False

    def test_add_album_contribution(self):
        """
        Add album contribution to an album this artist uploaded
        """
        data = {
            "artist_id": str(self.artist2.id),
            "album_id": str(self.album_id),
            "contribution_type": "Artist"
        }
        response = self.client.post(self.url, data, format="json", **self._get_headers(artist=True))

        # validate response
        self.assert201(response)
        self.assertReturnDict(response)

        # set state variables
        self.contrib_added = True
        self.contrib_id = response.data['contribution_id']

    def test_edit_album_contribution(self):
        """
        Edit an album contribution to an album this artist uploaded
        """
        # validate state
        if not self.contrib_added:
            self.test_add_album_contribution()
        if not self.contrib_added:
            self.fail("Could not validate that a contribution has been added")

        # send request
        data = {
            "contribution_id": self.contrib_id,
            "contribution_type": "Test Edit"
        }
        response = self.client.patch(self.url, data, format="json", **self._get_headers(artist=True))

        # validate response
        self.assert200(response)
        self.assertReturnDict(response)
        self.assertEqual(
            response.data['contribution_type'], AlbumContributor.objects.get(id=str(self.contrib_id)).contribution_type,
            msg="the returned contribution type was not updated in the database"
        )

    def test_edit_album_contribution_not_uploader(self):
        """
        Edit an album contribution to an album this artist did not upload

        Uses the second artist from the ArtistUserMixin to validate the request

        Sends two requests, first is sent while the uploading artist does not
        allow contribution edits, expecting 403.

        Second request is sent after changing that artist's settings to allow
        contributors to edit contributions, expecting 200.
        """
        # validate state
        if not self.contrib_added:
            self.test_add_album_contribution()
        if not self.contrib_added:
            self.fail("Could not validate that a contribution was added")
        
        # send request
        data = {
            "contribution_id": str(self.contrib_id),
            "contribution_type": "Test Edit 2"
        }
        response = self.client.patch(self.url, data, format="json", **self._get_headers(artist2=True))

        # validate response
        self.assert403(response)

        # send request with artist 1's settings changed
        self.artist.artist_profile.allow_contributors_to_edit_contributions = True
        self.artist.artist_profile.save()
        response = self.client.patch(self.url, data, format="json", **self._get_headers(artist2=True))

        # validate response
        self.assert200(response)
        self.assertReturnDict(response)
        self.assertEqual(
            response.data['contribution_type'], AlbumContributor.objects.get(id=str(self.contrib_id)).contribution_type,
            msg="the returned contribution type was not updated in the database"
        )

        # reset account setting
        self.artist.artist_profile.allow_contributors_to_edit_contributions = False
        self.artist.artist_profile.save()

    def test_get_album_contributions(self):
        """
        Get album contributions
        """
        response = self.client.get(self.url, format="json", **self._get_headers(artist=True))

        # validate response
        self.assert200(response)
        self.assertReturnList(response)
        for contrib in response.data:
            self.assertEqual(
                contrib['artist_id'], self.artist.id,
                msg="Not all contributions returned are this artist's contributions"
            )

    def test_delete_album_contribution(self):
        """
        Delete a contribution on a album this artist uploaded
        """
        # check state
        if not self.contrib_added:
            self.test_add_album_contribution()
        if not self.contrib_added:
            self.fail("Could not validate that a contribution waas created")

        # send request
        data = {
            "contribution_id": str(self.contrib_id)
        }
        response = self.client.delete(self.url, data, format="json", **self._get_headers(artist=True))

        # validate response
        self.assert204(response)
        self.assertEqual(
            0, AlbumContributor.objects.filter(id=str(self.contrib_id)).count(),
            msg="Still found the contribution in the database"
        )

    def test_delete_album_contribution_not_uploader(self):
        """
        Delete a contribution on an album this artist did not upload
        """
        # check state
        if not self.contrib_added:
            self.test_add_album_contribution()
        if not self.contrib_added:
            self.fail("Could not validate that a contribution waas created")

        # send request
        data = {
            "contribution_id": str(self.contrib_id)
        }
        response = self.client.delete(self.url, data, format="json", **self._get_headers(artist2=True))

        # validate response
        self.assert204(response)
        self.assertEqual(
            0, AlbumContributor.objects.filter(id=str(self.contrib_id)).count(),
            msg="Still found the contribution in the database"
        )
    
    def test_approve_album_contribution(self):
        """
        Approve a contribution
        """
        pass


class TestArtistSongContributions(RevibeTestCase):
    def setUp(self):
        self._get_application()
        self._get_user()
        self._get_artist_user()
        self._get_second_artist_user()
        self._create_song()
        self.url = reverse('artistaccount-song_contributions')

        _album = Album.objects.create(name="917834520", uploaded_by=self.artist, platform="Revibe")
        _album.save()
        self.album_id = _album.id

        _song = Song.objects.create(title="983pqhfg", duration=238, album=_album, uploaded_by=self.artist, platform="Revibe")
        _song.save()
        self.song_id = _song.id

        # state variables
        self.contrib_added = False

    def test_add_song_contribution(self):
        """
        Add song contribution to a song this artist uploaded
        """
        data = {
            "artist_id": str(self.artist2.id),
            "song_id": str(self.song_id),
            "contribution_type": "Test"
        }
        response = self.client.post(self.url, data, format="json", **self._get_headers(artist=True))

        # validate response
        self.assert201(response)
        self.assertReturnDict(response)

        # set state variables
        self.contrib_added = True
        self.contrib_id = response.data['contribution_id']

    def test_edit_song_contribution(self):
        """
        Edit a song contribution on a song this artist uploaded
        """
        # validate state
        if not self.contrib_added:
            self.test_add_song_contribution()
        if not self.contrib_added:
            self.fail("Could not validate that a contribution was created")

        # send request
        data = {
            "contribution_id": str(self.contrib_id),
            "contribution_type": "Test Edit"
        }
        response = self.client.patch(self.url, data, format="json", **self._get_headers(artist=True))

        # validate response
        self.assert200(response)
        self.assertReturnDict(response)
        self.assertEqual(
            response.data['contribution_type'], SongContributor.objects.get(id=str(self.contrib_id)).contribution_type,
            msg="the returned contribution type was not updated in the database"
        )

    def test_edit_song_contribution_not_uploader(self):
        """
        Edit a song contribution on a song this artist did not upload

        Sends two responses:
        First sends response when artist settings do not allow contributors to
        edit contributions; expect 403.

        Seconds sends response after updating settings to allow contributors to
        edit contributions; expect 200.
        """
        # check state
        if not self.contrib_added:
            self.test_add_song_contribution()
        if not self.contrib_added:
            self.fail("Could not validate that a contribution has been created")
        # send request
        data = {
            "contribution_id": str(self.contrib_id),
            "contribution_type": "Test Edit 2"
        }
        response = self.client.patch(self.url, data, format="json", **self._get_headers(artist2=True))

        # validate response
        self.assert403(response)

        # second request
        # change settings
        self.artist.artist_profile.allow_contributors_to_edit_contributions = True
        self.artist.artist_profile.save()

        # send request
        response = self.client.patch(self.url, data, format="json", **self._get_headers(artist2=True))

        # vaildate response
        self.assert200(response)
        self.assertReturnDict(response)
        self.assertEqual(
            response.data['contribution_type'], SongContributor.objects.get(id=str(self.contrib_id)).contribution_type,
            msg="the returned contribution type was not updated in the database"
        )

        # reset account settings
        self.artist.artist_profile.allow_contributors_to_edit_contributions = False
        self.artist.artist_profile.save()

    def test_get_song_contribution(self):
        """
        Get song contributions
        """
        # send request
        response = self.client.get(self.url, format="json", **self._get_headers(artist=True))

        # validate response
        self.assert200(response)
        self.assertReturnList(response)
        for contrib in response.data:
            self.assertEqual(
                contrib['artist_id'], self.artist.id,
                msg="Not all contributions returned are this artist's contributions"
            )

    def test_delete_song_contribution(self):
        """
        Delete a contribution on a song this artist uploaded
        """
        # check state
        if not self.contrib_added:
            self.test_add_song_contribution()
        if not self.contrib_added:
            self.fail("Could not validate that a contribution was created")

        # send request
        data = {
            "contribution_id": str(self.contrib_id)
        }
        response = self.client.delete(self.url, data, format="json", **self._get_headers(artist=True))

        # validate response
        self.assert204(response)
        self.assertEqual(
            0, SongContributor.objects.filter(id=str(self.contrib_id)).count(),
            msg="Still found the contribution in the database"
        )

    def test_delete_song_contribution_not_uploader(self):
        """
        Delete a contribution on a song this artist did not upload
        """
        # check state
        if not self.contrib_added:
            self.test_add_song_contribution()
        if not self.contrib_added:
            self.fail("Could not validate that a contribution was created")

        # send request
        data = {
            "contribution_id": str(self.contrib_id)
        }
        response = self.client.delete(self.url, data, format="json", **self._get_headers(artist2=True))

        # validate request
        self.assert204(response)
        self.assertEqual(
            0, SongContributor.objects.filter(id=str(self.contrib_id)).count(),
            msg="Still found the contribution in the database"
        )

    def test_approve_song_contribution(self):
        """
        Approve a contribution
        """
        pass


class EmailTestCase(RevibeTestCase):
    def setUp(self):
        self._get_application()
        self._get_user()
        self._get_artist_user()
        self.url = reverse('send-email')
    
    def test_send_artist_invite_email(self):
        # send request
        data = {}
        response = self.client.post(self.url, data, format="json", **self._get_headers(artist=True))

        # validate request
        self.assert503(response)


class TagSongsTestCase(RevibeTestCase):
    def setUp(self):
        self._get_application()
        self._get_user()
        self._get_artist_user()
        self._create_song()
        self.url = reverse('artistaccount-tag_song')
    
    def test_add_tag(self):
        # send request
        data = {}
        response = self.client.post(self.url, data, format="json", **self._get_headers(artist=True))

        # validate request
        self.assert201(response)


