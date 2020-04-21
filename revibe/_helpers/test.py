"""
Author: Jordan Prechac
Created: 07 Jan, 2020
"""

from django.db.utils import IntegrityError
from django.urls import reverse
from rest_framework.test import APITestCase, APIClient
from rest_framework.utils.serializer_helpers import ReturnList, ReturnDict
from oauth2_provider.models import Application

import datetime
import io
from PIL import Image as PILImage
import sys

from revibe._helpers import status

from accounts.models import CustomUser, Profile, ArtistProfile
from administration.models import Alert, Blog, Campaign, YouTubeKey, Variable
from content.models import *

# -----------------------------------------------------------------------------
# mixins

class TestStatusMixin:
    def _get_code(self, arg1):
        """
        Allows test cases to send a status code or the response object to all
        assert status code methods.
        """
        # check if sent a status code directly
        if type(arg1) == int:
            return arg1
        # check if sent a response with a valid status code
        elif type(arg1.status_code) == int:
            return arg1.status_code
        # check if the status code was somehow sent as some other object that \
        # can be cast as a string
        else:
            try:
                return int(arg1)
            except ValueError:
                pass

        raise ValueError(f"Could not find a status code in object: {arg1}")

    def _assert_status_code(self, arg, status, *args, **kwargs):
        """
        Where the magic happens...
        Makes sure it has an integer from the response and does the comparison.
        """
        if 'msg' not in kwargs.keys():
            kwargs['msg'] = f"Response status code is not {status}"

        arg = self._get_code(arg)
        self.assertEqual(arg, status, *args, **kwargs)

    # 2xx
    def assert200(self, arg1, *args, **kwargs):
        self._assert_status_code(arg1, 200)

    def assert201(self, arg1, *args, **kwargs):
        self._assert_status_code(arg1, 201)

    def assert204(self, arg1, *args, **kwargs):
        self._assert_status_code(arg1, 204)
    
    # 4xx
    def assert400(self, arg1, *args, **kwargs):
        self._assert_status_code(arg1, 400)

    def assert401(self, arg1, *args, **kwargs):
        self._assert_status_code(arg1, 401)

    def assert403(self, arg1, *args, **kwargs):
        self._assert_status_code(arg1, 403)

    def assert404(self, arg1, *args, **kwargs):
        self._assert_status_code(arg1, 404)

    def assert409(self, arg1, *args, **kwargs):
        self._assert_status_code(arg1, 409)
    
    def assert417(self, arg1, *args, **kwargs):
        self._assert_status_code(arg1, 417)

    # 5xx
    def assert501(self, arg1, *args, **kwargs):
        self._assert_status_code(arg1, 501)

    def assert503(self, arg1, *args, **kwargs):
        self._assert_status_code(arg1, 503)

    def assert512(self, arg1, *args, **kwargs):
        self._assert_status_code(arg1, 512)

    def assert513(self, arg1, *args, **kwargs):
        self._assert_status_code(arg1, 513)


class TestTypeMixin:
    def _get_response_data(self, obj):
        if hasattr(obj, 'data'):
            # return type of response.data
            return obj.data
        else:
            # return type of data from response.data
            return obj

    def assertReturnDict(self, arg, *args, **kwargs):
        self._perform_assertion(
            arg, dict, *args, **kwargs
        )
    def assertReturnList(self, arg, *args, **kwargs):
        self._perform_assertion(
            arg, list, *args, **kwargs
        )
    
    def _perform_assertion(self, arg, check, *args, **kwargs):
        """
        Checks that the arg is of the same class or a subclass of the check
        value.
        """
        arg = self._get_response_data(arg)

        if 'msg' not in kwargs.keys():
            kwargs['msg'] = "{} is not of type {}".format(str(arg), str(check))
        
        self.assertTrue(
            isinstance(arg, check),
            *args, **kwargs
        )


class BaseRevibeTestMixin:
    def _get_application(self):
            try:
                Application.objects.create(client_type="confidential", authorization_grant_type="password", name="Revibe First Party Application")
            except Exception as e:
                raise e

    def _get_headers(self, sper=False, artist=False, artist2=False, other=None):
        token = self.access_token
        if sper:
            token = self.super_access_token
        elif artist:
            token = self.artist_access_token
        elif artist2:
            token = self.artist_access_token2
        elif other is not None:
            token = other
        return {"Authorization": "Bearer {}".format(token)}
    
    def generate_image(self):
        file = io.BytesIO()
        image = PILImage.new('RGBA', (100,100), color=(155,0,0))
        image.save(file, 'png')
        file.name = 'test.png'
        file.seek(0)
        return file


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
            raise e

        # create the user's artist
        if not user.artist:
            try:
                artist = Artist.objects.create(name="Testing Artist", platform="Revibe")

                artist_profile = ArtistProfile.objects.create(country="Fake Country", city="Fake City", artist=artist)
                artist_profile.save()

                user.artist = artist
                user.save()
            except Exception as e:
                raise e

        login = client.post(reverse('login'), {"username": "johnartist","password": "password","device_type": "browser",}, format="json")
        self.artist_user = user
        self.artist = artist
        self.artist_access_token = login.data['access_token']
    
    def _get_second_artist_user(self):
        client = APIClient()

        # create the user
        try:
            user = CustomUser.objects.create_user(username="artist2",password="password")
            profile = Profile.objects.create(country="US", user=user)
            profile.save()
            user.save()
        except IntegrityError as ie:
            user = CustomUser.objects.get(username="artist2")
        except Exception as e:
            raise e
    
        # create the artist
        if not user.artist:
            try:
                artist = Artist.objects.create(name="Second Artist", platform="Revibe")

                artist_profile = ArtistProfile.objects.create(country="Fake", artist=artist)
                artist_profile.save()
                artist.save()

                user.artist = artist
                user.is_artist = True
                user.save()
            except Exception as e:
                raise e
        
        login = client.post(reverse('login'), {"username":"artist2", "password":"password","device_type":"browser"}, format="json")
        self.artist_user2 = user
        self.artist2 = artist
        self.artist_access_token2 = login.data['access_token']


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
        # create the artist
        self.content_artist = Artist.objects.create(name="Test Artist Content", platform="Revibe")

        # create their artist profile
        ArtistProfile.objects.create(artist=self.content_artist, allow_revibe_website_page=True)

        return self.content_artist

    def _create_album(self):
        artist = self.content_artist if hasattr(self, 'content_artist') else self._create_artist()
        self.content_album = Album.objects.create(name="Test Album Content", platform="Revibe", uploaded_by=artist)
        AlbumContributor.objects.create(artist=artist, album=self.content_album, contribution_type="Artist", primary_artist=True)
        return self.content_album
    
    def _create_song(self):
        artist = self.content_artist if hasattr(self, 'content_artist') else self._create_artist()
        album = self.content_album if hasattr(self, 'content_album') else self._create_album()
        self.content_song = Song.objects.create(title="Test Song Content", genre="Hip Hop", album=album, uploaded_by=artist, platform="Revibe")
        SongContributor.objects.create(artist=artist, song=self.content_song, contribution_type="Artist", primary_artist=True)
        return self.content_song


class MusicMixin:
    pass


class AdministrationMixin:
    def _get_campaign(self):
        try:
            total = Campaign.object.get(name="example campaign")
        except Exception:
            campaign = Campaign.objects.create(name="example campaign", budget=0, spent=0)
            campaign.save()
        self.campaign = campaign

    def _get_youtube_key(self):
        try:
            key = YouTubeKey.objects.get(key="hellooooooooooooo")
        except Exception:
            key = YouTubeKey.objects.create(key="hellooooooooooooo")

        self.key = key
    
    def _get_alert(self):
        try:
            alert = Alert.objects.get(subject="111")
        except Exception:
            start = datetime.datetime.now() - datetime.timedelta(days=30)
            end = datetime.datetime.now() + datetime.timedelta(days=30)
            alert = Alert.objects.create(subject="111", message="alert message", category=Alert._category_choices[0][0], enabled=True, start_date=start, end_date=end)
        
        self.alert = alert
    
    def _get_blog(self):
        try:
            blog = Blog.objects.get(title="test1")
        except Exception:
            publish = datetime.date.today() - datetime.timedelta(days=1)
            blog = Blog.objects.create(category="other", title="test1", body="test1", publish_date=publish, author=self.superuser)
        self.blog = blog
    
    def _get_variable(self):
        try:
            variable = Variable.objects.get()
        except Exception:
            variable = Variable.objects.create(key="testing", value="testing value thing")
        self.variable = variable


class MetricsMixin:
    pass


# -----------------------------------------------------------------------------
# classes

class BaseRevibeTestCase(
    APITestCase, BaseRevibeTestMixin, TestStatusMixin, TestTypeMixin
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

