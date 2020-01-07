"""
Author: Jordan Prechac
Created: 07 Jan, 2020
"""

from django.db.utils import IntegrityError
from django.urls import reverse
from rest_framework.test import APITestCase, APIClient
from oauth2_provider.models import Application

from revibe._helpers import status

from accounts.models import CustomUser, Profile, ArtistProfile
from content.models import *

# -----------------------------------------------------------------------------
# mixins

class TestStatusMixin:
    def assert200(self, arg1):
        self.assertEqual(arg1, status.HTTP_200_OK)
    
    def assert201(self, arg1):
        self.assertEqual(arg1, status.HTTP_201_CREATED)
    
    def assert204(self, arg1):
        self.assertEqual(arg1, status.HTTP_204_NO_CONTENT)


class BaseRevibeTestMixin:
    def _get_application(self):
            try:
                Application.objects.create(client_type="confidential", authorization_grant_type="password", name="Revibe First Party Application")
            except Exception as e:
                raise e

    def _get_headers(self, sper=False, artist=False):
        token = self.access_token
        if sper:
            token = self.super_access_token
        elif artist:
            token = self.artist_access_token
        return {"Authorization": "Bearer {}".format(token)}


class AuthorizedUserMixin:
    def _get_user(self):
        client = APIClient()
        try:
            # user = CustomUser.objects.create_user(username="johnsnow", password="password")
            # profile = Profile.objects.create(country="US", user=user)
            # profile.save()
            # user.save()
            response = self.client.post(reverse('register'), {
                "username": "johnsnow",
                "password": "password",
                "device_type": "browser",
                "profile": {},
            }, format="json")
            user = CustomUser.objects.get(username=response.data['user']['username'])
        except IntegrityError as ie:
            user = CustomUser.objects.get(username="johnsnow")
        except Exception as e:
            raise(e)
        login = client.post(reverse('login'), {"username": "johnsnow","password": "password","device_type": "phone",}, format="json")
        self.user = user
        self.access_token = login.data['access_token']
        self.refresh_token = login.data['refresh_token']


class ArtistUserMixin:
    def _get_artist_user(self):
        client = APIClient()

        # create the user
        try:
            user = CustomUser.objects.create_user(username="johnartist", password="password")
            profile = Profile.objects.create(country="US", user=user)
            profile.save()
            user.save()
        except IntegrityError as ie:
            user = CustomUser.objects.get(username="johnartist")
        except Exception as e:
            raise(e)

        # create the user's artist
        if not user.artist:
            try:
                artist = Artist.objects.create(name="Testing Artist")

                artist_profile = ArtistProfile.objects.create(country="Fake Country", city="Fake City", artist=artist)
                artist_profile.save()

                user.artist = artist
                user.save()
            except Exception as e:
                raise e

        login = client.post(reverse('login'), {"username": "johnartist","password": "password","device_type": "browser",}, format="json")
        self.artist_user = user
        self.artist_access_token = login.data['access_token']


class SuperUserMixin:
    def _get_superuser(self):
        try:
            user = CustomUser.objects.create_superuser("admin","admin@admin.com","admin")
            profile = Profile.objects.create(user=user)
            user.is_staff = True
            user.save()
            profile.save()
        except IntegrityError as ie:
            user = CustomUser.objects.get(username="admin")
        except Exception as e:
            raise e

        login = self.client.post(reverse('login'), {"username": "admin","password": "admin","device_type": "browser",}, format="json")
        self.superuser = user
        self.super_access_token = login.data['access_token']


class ContentMixin:
    def _create_artist(self):
        self.artist = Artist.objects.create(name="Test Artist Content", platform="Revibe")
        return self.artist

    def _create_album(self):
        artist = self.artist if hasattr(self, 'artist') else self._create_artist()
        self.album = Album.objects.create(name="Test Album Content", platform="Revibe", uploaded_by=artist)
        AlbumContributor.objects.create(artist=artist, album=self.album, contribution_type="Artist", primary_artist=True)
        return self.album
    
    def _create_song(self):
        artist = self.artist if hasattr(self, 'artist') else self._create_artist()
        album = self.album if hasattr(self, 'album') else self._create_album()
        self.song = Song.objects.create(title="Test Song Content", genre="Hip Hop", album=album, uploaded_by=artist, platform="Revibe")
        SongContributor.objects.create(artist=artist, song=self.song, contribution_type="Artist", primary_artist=True)
        return self.song


class MusicMixin:
    pass


class AdministrationMixin:
    pass


class MetricsMixin:
    pass


# -----------------------------------------------------------------------------
# classes

class BaseRevibeTestCase(
    APITestCase, BaseRevibeTestMixin, TestStatusMixin
):
    """
    Basis for all of our Test Cases
    Provides the basis for getting applications for tokens and the status code checks for most requests.
    """
    pass


class AuthorizedAPITestCase(
    BaseRevibeTestCase, AuthorizedUserMixin, SuperUserMixin, ArtistUserMixin
):
    """
    Builds on the basic BaseRevibeTestCase functionality by adding authentication methods.
    """
    pass


class RevibeTestCase(
    AuthorizedAPITestCase, ContentMixin, MusicMixin, AdministrationMixin, MetricsMixin
):
    """
    Combines the Authentication functionality with objects from each of the apps.
    """
    pass

