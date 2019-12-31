from django.urls import reverse
from rest_framework.test import APITestCase, APIClient
from oauth2_provider.models import Application

from accounts.models import CustomUser, Profile, ArtistProfile
from content.models import *

class BaseRevibeTestMixin:
    def _get_application(self):
            try:
                Application.objects.create(client_type="confidential", authorization_grant_type="password", name="Revibe First Party Application")
            except Exception as e:
                raise e

    def _get_headers(self):
        return {"Authorization": "Bearer {}".format(self.access_token)}

class AuthorizedUserMixin:
    def _get_user(self):
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

        login = client.post(reverse('login'), {"username": "johnartist","password": "password","device_id": "1234567890","device_name": "Django Test Case","device_type": "browser",}, format="json")
        self.artist_user = user
        self.access_token = login.data['access_token']

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

        login = self.client.post(reverse('login'), {"username": "admin","password": "admin","device_id": "1234567890admin","device_name": "Django Test Case","device_type": "browser",}, format="json")
        self.superuser = user
        self.access_token = login.data['access_token']


class AuthorizedAPITestCase(
    APITestCase, BaseRevibeTestMixin, AuthorizedUserMixin, SuperUserMixin, ArtistUserMixin
):
    """
    Combines functionality of multiple header and authorization classes
    """
    pass


# content-specific mixins
class CreateContentMixin:
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
        self.song = Song.objects.create(title="Test Song Content", genre="Hip Hop", album=album, uploaded_by=artist)
        SongContributor.objects.create(artist=artist, song=self.song, contribution_type="Artist", primary_artist=True)
        return self.song

class AuthorizedContentAPITestCase(
    AuthorizedAPITestCase, CreateContentMixin
):
    """
    Combines the base Authorized Test Case class with the content-creation functionality. 
    """
    pass

