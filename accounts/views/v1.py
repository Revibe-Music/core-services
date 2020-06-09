from django.conf import settings
from django.contrib.auth.models import AnonymousUser
from django.core.exceptions import MultipleObjectsReturned, ObjectDoesNotExist
from django.core.mail import send_mail, send_mass_mail
from django.db import IntegrityError
from django.http import HttpRequest
from django.template.loader import render_to_string
from django.views.decorators.csrf import csrf_exempt
from django.utils import timesince
from django.utils.decorators import method_decorator
from django.utils.html import strip_tags
from rest_framework import viewsets, permissions, generics, status
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.exceptions import ValidationError, APIException
from rest_framework.response import Response
from rest_auth.registration.views import SocialConnectView, SocialLoginView
from oauth2_provider.views import TokenView, RevokeTokenView
from oauth2_provider.contrib.rest_framework import TokenHasReadWriteScope,TokenMatchesOASRequirements, TokenHasScope
from oauth2_provider.models import Application, AccessToken, RefreshToken
from oauthlib import common
from allauth.socialaccount.providers.facebook.views import FacebookOAuth2Adapter
from allauth.socialaccount.providers.google.views import GoogleOAuth2Adapter
from allauth.socialaccount.providers.spotify.views import SpotifyOAuth2Adapter
from allauth.socialaccount.providers.oauth2.client import OAuth2Client
from allauth.socialaccount.models import SocialAccount, SocialToken, SocialApp

import datetime
import json
import requests

from logging import getLogger
logger = getLogger(__name__)

from revibe.auth.artist import get_authenticated_artist
from revibe.viewsets import GenericPlatformViewSet
from revibe.utils import mailchimp
from revibe.utils.params import get_url_param
from revibe._errors import accounts ,network
from revibe._errors.accounts import AccountNotFound, NotArtistError
from revibe._errors.network import ConflictError, ForbiddenError, NotImplementedError, ExpectationFailedError
from revibe._helpers import responses, const

from accounts.adapter import TokenAuthSupportQueryString
from accounts.artist.analytics import BarChart, CardChart, LineChart
from accounts.exceptions import AccountsException, PasswordValidationError, AuthError
from accounts.permissions import TokenOrSessionAuthentication
from accounts.models import *
from accounts.referrals.tasks import add_referral_points
from accounts.serializers.v1 import *
from accounts.utils.auth import change_password, reset_password, generate_tokens, refresh_access_token
from accounts.utils.models import register_new_user
from accounts._helpers import validation
from administration.models import Campaign
from content.models import Album, Song, SongContributor, AlbumContributor,PlaceholderContribution
from content.serializers import v1 as content_ser_v1
from content.utils.analytics import calculate_advanced_song_analytics, calculate_unique_monthly_listeners
from content.utils.models import (
    # placeholder contribs
    create_permananent_contribs, create_placeholder,

    # tag stuff
    add_tag_to_song, remove_tag_from_song, add_tag_to_album, remove_tag_from_album,
    # genre stuff
    add_genres_to_object, remove_genres_from_object
)
from customer_success.decorators import attributor
from metrics.models import Stream
from music.models import *
from music.serializers import v1 as music_ser_v1
from notifications.decorators import notifier

# -----------------------------------------------------------------------------

def get_device(data):
    """
    Takes in request data, spits out a device object
    """
    try:
        device = Device.objects.get(device_id=data['device_id'],device_type=data['device_type'])
    except ObjectDoesNotExist:
        device = Device(
            device_id = data['device_id'],
            device_type = data['device_type'],
            device_name = data['device_name']
        )
        device.save()
    except MultipleObjectsReturned:
        device = Device.objects.filter(device_id=data['device_id'],device_type=data['device_type'])[0]
    except Exception as e:
        raise e
    return device

def create_libraries(user):
    assert isinstance(user, CustomUser), "must pass a user to 'create_libraries()'"
    default_libraries = [const.REVIBE_STRING, const.YOUTUBE_STRING]
    for def_lib in default_libraries:
        Library.objects.create(platform=def_lib, user=user)

    # check that it worked
    if len(Library.objects.filter(user=user)) < 2:
        raise ValidationError("Error creating libraries")


@method_decorator(csrf_exempt, name="dispatch")
class RegistrationAPI(generics.GenericAPIView):
    """
    this works when application has following attributes:
    client type: confidential
    Authorization grant type: Resource owner password-based
    curl -X POST -d "client_id=y2iPQuosC9qgIJZua9w5VCpHMTdO7Onkl2RF9qQk&client_secret=KE5IMAxQizJAwRKkKUY244PctidKPL88mQwyGPX6ci9ZymHsYSgxxTLeJNMppf1lerlNfjQnKYpZ1xzlsRFtdV6S9gLfb6WdFnVu29BSw8lteoqiU6ZoJtnxabs4slgs&grant_type=password&username=rileystephens&password=Reed1rile2" http://127.0.0.1:8000/o/token/
    """
    serializer_class = UserSerializer
    permission_classes = [permissions.AllowAny]


    @notifier(trigger="register", user_after_request=True, force=True, medium="email")
    def post(self, request, *args, **kwargs):
        data = request.data
        params = request.query_params
        old_user = request.user if not isinstance(request.user, AnonymousUser) else None

        # perform registration
        add_artist = True if request.data.get('device_type', None) == 'browser' else False
        register_data = register_new_user(data, params, old_user, request=request, add_artist=add_artist, *args, **kwargs)

        # format the data from register_new_user
        return_data = {
            "user": UserSerializer(instance=register_data['user']).data,
            "access_token": register_data['access_token'].token
        }
        if "refresh_token" in register_data.keys():
            return_data.update({"refresh_token": register_data['refresh_token'].token})

        return responses.CREATED(data=return_data), register_data['user']


@method_decorator(csrf_exempt, name="dispatch")
class LoginAPI(generics.GenericAPIView):
    permission_classes = [permissions.AllowAny]
    serializer_class = LoginAccountSerializer

    @attributor(name="Login Artist Portal", methods=['post'], user_target="data.user.user_id")
    @attributor(name="Login Mobile App", methods=['post'], user_target="data.user.user_id")
    def post(self, request, *args, **kwargs):
        login_data = {
            "username": request.data['username'],
            "password": request.data['password'],
        }
        serializer = self.get_serializer(data=login_data)
        if serializer.is_valid():
            device = request.data['device_type']

            user = serializer.validated_data

            add_artist = True if device == 'browser' else False
            access_token, refresh_token = generate_tokens(user, request, use_default_app=True, delete_old_tokens=True, add_artist=add_artist)

            user.last_login = timezone.now()
            user.save()

            data = {
                "user": UserSerializer(user, context=self.get_serializer_context()).data,
                "access_token": access_token.token,
            }

            if device != 'browser':
                data.update({"refresh_token": refresh_token.token})

            return Response(data, status=status.HTTP_200_OK)

        else:
            return responses.SERIALIZER_ERROR_RESPONSE(serializer)

        return responses.DEFAULT_400_RESPONSE()


@method_decorator(csrf_exempt, name="dispatch")
class RefreshTokenAPI(generics.GenericAPIView):
    permission_classes = [permissions.AllowAny]
    serializer_class = RefreshTokenSerializer

    def post(self, request, *args, **kwargs):
        # check expectations
        required_fields = ['refresh_token','device_type']
        for key in request.data.keys():
            if key not in required_fields:
                err = f"Unexpected field: {key} in request data."
                return responses.SERIALIZER_ERROR_RESPONSE(detail=err)
        for field in required_fields:
            if field not in request.data.keys():
                err = f"Missing field: {field} in request data."
                return responses.SERIALIZER_ERROR_RESPONSE(detail=err)

        # get tokens
        try:
            access_token = refresh_access_token(request.data['refresh_token'])
        except AuthError:
            raise network.BadEnvironmentError("This account has been logged in on another device, please log in again")

        user = access_token.user
        user.last_login = timezone.now()
        user.save()

        return Response({"access_token": access_token.token}, status=status.HTTP_200_OK)


class LogoutAPI(generics.GenericAPIView, RevokeTokenView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = AccessTokenSerializer

    def post(self, request, *args, **kwargs):
        token = AccessToken.objects.get(token=request.data['access_token'])

        # send back an issue if server could not find the user
        if not token.user:
            return responses.UNAUTHORIZED(detail="could not identify the current user")
        elif token.user != request.user:
            return responses.NOT_PERMITTED(detail="could not identify the current user as the owner of this token")

        token.refresh_token.delete()
        token.delete()

        return responses.OK(detail="logout successful")


class LogoutAllAPI(generics.GenericAPIView):
    permission_classes = [permissions.IsAuthenticated]

    @notifier(trigger='logout-all', force=True, medium='email')
    def post(self, request, *args, **kwargs):
        user = request.user

        # delete all user's access tokens
        tokens = AccessToken.objects.filter(user=user)
        num = len(tokens)
        tokens.delete()

        # extra check to catch hanging refresh tokens as well
        tokens = RefreshToken.objects.filter(user=user)
        num += len(tokens)
        tokens.delete()

        return Response({"detail": "logout-all successful", "tokens deleted": num}, status=status.HTTP_200_OK)


class SendRegisterLink(generics.GenericAPIView):
    permission_classes = [permissions.IsAuthenticated]

    register_link = "http://artist.revibe.tech/account/register"

    def get_register_link(self, user):
        return f"{self.register_link}?uid={user.id}"

    def __init__(self, *args, **kwargs):
        super(SendRegisterLink, self).__init__(*args, **kwargs)
        self.types_of_emails = {
            'artist_invite':  'artist_invite_email',# general invite for artists
            'contribution': 'contribution_invite_email_white', # invite for contributions, white background
            'contribution_black': 'contribution_invite_email_black', # invite for contributions, black background
        }

    def post(self, request, *args, **kwargs):
        """
        Required fields:
        to: (list) the emails to send mail to
        artist: (bool) coming from an artist function or not (like the Artist Portal)
        type: (string) the type of invite to send,
            must be one of 'artist_invite', 'contribution', 'contribution_black'
        """
        # only send emails when in the cloud
        if not settings.USE_S3:
            raise network.BadEnvironmentError()

        # validate data
        self._validate_request(request)

        # configure recipients
        to = self._get_recipients(request)

        # determine what kind of email it is and call the function
        num_sent = self.configure_email(request, to, *args, **kwargs)

        info = {
            "total requested": len(to),
            "total sent": num_sent,
            "not sent": len(to) - num_sent,
        }

        return responses.OK(data=info)

    def configure_email(self, request, recipients, subject=None, *args, **kwargs):
        """
        """
        user = request.user
        if getattr(user, 'artist', None) == None:
            raise accounts.NotArtistError()

        name = user.artist.name
        subject = f"{name} has invited you to join Revibe" if subject == None else subject
        from_address = f'"Join Revibe" <{const.ARTIST_FROM_EMAIL}>'

        # get the html message
        context = {
            "name": name,
            "register_link": self.get_register_link(user),
            "revibe_medium_image": const.REVIBE_MEDIUM_IMAGE,
            "youtube_image": const.YOUTUBE_IMAGE,
            "twitter_image": const.TWITTER_IMAGE,
            "facebook_image": const.FACEBOOK_IMAGE,
            "instagram_image": const.INSTAGRAM_IMAGE,
        }
        html_message = render_to_string(f"accounts/{self.types_of_emails[request.data['type']]}.html", context=context)

        # send the mail
        num_sent = self._send_emails(subject, html_message, from_address, recipients)

        return num_sent

    def _send_emails(self, subject, html_message, from_address, recipient_list, fail_silently=True, *args, **kwargs):
        """
        function that actually sends the messages.
        """
        plain_message = strip_tags(html_message)

        num_sent = 0
        for rec in recipient_list:
            num_sent += send_mail(
                subject=subject,
                message= plain_message,
                from_email=from_address,
                recipient_list=[rec,],
                html_message= html_message,
                fail_silently=fail_silently
            )

        return num_sent

    def _get_recipients(self, request):
        """
        helper function to return a list of valid strings
        """
        # do not need to validate that 'to' is in request.data, this should
        # only ever be called after validating the request

        to = request.data['to']
        to = to if isinstance(to, list) else [to,]

        # maybe validate email addresses later?
        return to

    def _validate_request(self, request):
        """
        """
        errors = {}

        # validate fields
        required_fields = ['to','type']
        alt_fields = ['artist']
        for key in request.data.keys():
            if key not in required_fields and key not in alt_fields:
                errors[key] = f"Got an unexpected value: {key}"
        for field in required_fields:
            if field not in request.data.keys():
                errors[field] = f"Must include {field} in request"

        # valiadate email type
        t = request.data['type']
        if t not in self.types_of_emails.keys():
            errors['type'] = f"Cannot determine what kind of email to send from type: {t}"

        # return errors if there are any, otherwise move on
        if len(errors) > 0:
            raise ExpectationFailedError(detail=errors)
        return True


class GoogleLogin(SocialLoginView):
    """
    Creates user from Google profile or logs user in from Google profile
    """
    adapter_class = GoogleOAuth2Adapter
    client_class = OAuth2Client

    @property
    def callback_url(self):
        method = "http://"
        root = ""
        if settings.DEBUG == False:
            # production
            method = "https://"
            root = "api.revibe.tech"
        elif settings.USE_S3 == True:
            # test
            root = "test-env.myrpupud2p.us-east-2.elasticbeanstalk.com"
        else:
            # local
            root = "127.0.0.1:8000"

        return f"{method}{root}/v1/account/google-authentication/callback/"

    @notifier(trigger="social-register", force=True, medium='email', skip_first=True)
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)


class FacebookLogin(SocialLoginView):
    """
    """
    adapter_class = FacebookOAuth2Adapter
    client_class = OAuth2Client

    @property
    def callback_url(self):
        method = "http://"
        root = ""
        if settings.DEBUG == False:
            # production
            method = "https://"
            root = "api.revibe.tech"
        elif settings.USE_S3 == True:
            # test
            root = "test-env.myrpupud2p.us-east-2.elasticbeanstalk.com"
        else:
            # local
            root = "127.0.0.1:8000"

        return f"{method}{root}/v1/account/facebook-authentication/callback/"

    @notifier(trigger="social-register", force=True, medium='email', skip_first=True)
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)


# Linked Account Views

class SpotifyConnect(SocialConnectView):
    """ Logs already authenticated user into Spotify account """
    adapter_class = SpotifyOAuth2Adapter
    callback_url = 'revibeapp://callback'
    client_class = OAuth2Client

    def get_response(self):
        """
            This method overrides the get_response method in the LoginView class
            located in rest_auth/views.py. This method is responsible for returning a response
            and in this case we want to return a user's spotify access token ad refresh token.
        """
        serializer_class = self.get_response_serializer()
        if getattr(settings, 'REST_USE_JWT', False):
            data = {'user': self.user, 'token': self.token}
            serializer = serializer_class(instance=data, context={'request': self.request})
        else:
            serializer = serializer_class(instance=self.token, context={'request': self.request})
        social_account = SocialAccount.objects.get(user=self.user,provider="spotify")
        spotify_token = SocialToken.objects.get(account=social_account)
        return Response({'access_token':spotify_token.token,'refresh_token':spotify_token.token_secret,"expires_in": 3600}, status=status.HTTP_200_OK)

    @notifier(trigger="spotify-connect", force=True, medium='email')
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)


@method_decorator(csrf_exempt, name="dispatch")
class SpotifyRefresh(generics.GenericAPIView):
    permission_classes = [permissions.AllowAny]
    authentication_classes = [TokenAuthSupportQueryString]
    required_alternate_scopes = {
        'GET': [['ADMIN'], ['first-party']],
        'POST': [['ADMIN'], ['first-party']]
    }
    serializer_class = RefreshTokenSerializer

    def post(self, request, *args, **kwargs):
        # should spotify refresh token be verified against user?
        serializer = self.get_serializer(data=request.data)
        if not serializer.is_valid():
            raise network.ExpectationFailedError(detail=serializer.errors)

        refresh_token = serializer.validated_data['refresh_token']
        if SocialToken.objects.filter(token_secret=refresh_token).exists():
            token = SocialToken.objects.get(token_secret=refresh_token)
            spotify = SocialApp.objects.get(name="Spotify")
            try:
                spotifyurl = "https://accounts.spotify.com/api/token"
                spotifydata = {'grant_type': 'refresh_token', 'refresh_token':token.token_secret}
                response = requests.post(spotifyurl, data=spotifydata, auth=(spotify.client_id, spotify.secret))
                response = json.loads(response.text)
                token.token = response['access_token']
                token.save()
                return Response({'access_token':response['access_token'],'refresh_token':token.token_secret, "expires_in": 3600}, status=status.HTTP_200_OK)
            except:
                return Response({'access_token': token.token,'refresh_token':token.token_secret}, status=status.HTTP_200_OK)

        return Response({"error":"Social Token does not exist."},status=status.HTTP_400_BAD_REQUEST) # should probably return current tokens


@method_decorator(csrf_exempt, name="dispatch")
class SpotifyLogout(generics.GenericAPIView):
    permission_classes = [TokenOrSessionAuthentication]
    required_alternate_scopes = {
        'GET': [['ADMIN'], ['first-party']],
        'POST': [['ADMIN'], ['first-party']]
    }

    @notifier(trigger="spotify-disconnect", force=True, medium='email')
    def post(self, request, *args, **kwargs):
        if SocialAccount.objects.filter(user=request.user,provider="spotify").exists():
            social_account = SocialAccount.objects.get(user=request.user,provider="spotify")
            social_account.delete()
            return Response({'message':'Spotify logout successful.'}, status=status.HTTP_200_OK)
        return Response({"error":"User has not logged into Spotify."},status=status.HTTP_400_BAD_REQUEST) # should probably return current tokens


class UserLinkedAccounts(viewsets.ModelViewSet):
    serializer_class = SocialTokenSerializer
    permission_classes = [TokenOrSessionAuthentication]
    required_alternate_scopes = {
        "GET": [["ADMIN"],["first-party"]],
    }

    def get_queryset(self):
        """
        Return the list of saved songs for the current user
        """
        user = self.request.user
        return SocialToken.objects.filter(account__user=user)


# Artist Account API Views

class UserArtistViewSet(GenericPlatformViewSet):
    """
    Contains the core functionality for the Artist Portal
    """
    platform = 'Revibe'
    queryset = CustomUser.objects.all()
    serializer_class = UserArtistSerializer
    permission_classes = [TokenOrSessionAuthentication]
    required_alternate_scopes = { # TODO: add 'artist' along with 'first-party'
        'GET': [['ADMIN'],['first-party']],
        'POST': [['ADMIN'],['first-party']],
        'PATCH': [['ADMIN'],['first-party']],
        'PUT': [['ADMIN'],['first-party']],
        'DELETE': [['ADMIN'],['first-party']],
    }

    def list(self, request, *args, **kwargs):
        artist = self.get_current_artist(request)

        artist = self.serializer_class(artist, context=self.get_serializer_context())
        return responses.OK(serializer=artist)

    @notifier(
        trigger="create-artist-profile",
        force=True,
        medium='email', artist=True
    )
    def create(self, request, *args, **kwargs):
        """
        Creates an Artist Profile
        """
        kwargs['context'] = self.get_serializer_context()
        # check if user already has an artist object
        if request.user.artist != None:
            return responses.CONFLICT(detail="this user already has an artist profile")

        # set data platform
        if 'platform' not in request.data.keys():
            _mutable = request.data._mutable
            request.data._mutable = True
            request.data['platform'] = 'Revibe'
            request.data._mutable = _mutable

        # create the artist and attach to the user
        serializer = self.serializer_class(data=request.data, *args, **kwargs)
        if not serializer.is_valid():
            return responses.SERIALIZER_ERROR_RESPONSE(serializer)

        artist = serializer.save()

        # attach artist to user
        request.user.artist = artist
        request.user.is_artist = True
        request.user.save()

        # check placeholder contributions
        create_permananent_contribs(artist)

        # add referral points
        try:
            add_referral_points.s(request.user.id, "create_artist_profile", datetime.datetime.now()).delay()
        except Exception:
            pass

        if not settings.DEBUG:
            try:
                mailchimp.update_list_member(artist.artist_user, artist=True)
            except Exception:
                pass

        return responses.CREATED(serializer)

    def patch(self, request, *args, **kwargs):
        instance = self.get_current_artist(request)
        serializer = self.get_serializer(data=request.data, instance=instance, partial=True)
        if serializer.is_valid():
            serializer.save()
            return responses.UPDATED(serializer=serializer)
        else:
            return responses.SERIALIZER_ERROR_RESPONSE(serializer=serializer)
        return responses.DEFAULT_400_RESPONSE()

    def get_current_artist(self, request):
        return get_authenticated_artist(request)

    def check_contrib_permissions(self, artist, instance, rel):
        """
        Checks settings and permissions to validate that the current request is
        valid.
        """
        assert type(rel) == str, "'rel' must be a string object"
        assert rel in ['song','album'], "'rel' must be 'song' or 'album'"

        if not hasattr(instance, rel):
            raise Exception("Could not find the contribution's '{}'".format(rel))
        content = getattr(instance, rel)

        # define variables
        contributor = instance.artist
        uploader = content.uploaded_by
        allow_contrib_edit = uploader.artist_profile.allow_contributors_to_edit_contributions

        if artist == uploader:
            return True

        if artist != contributor:
            raise ForbiddenError("You cannot edit this contribution")

        if not allow_contrib_edit:
            raise ForbiddenError("{} does not allow contributors to edit contributions".format(str(uploader)))

        return True

    def check_delete_permissions(self, artist, instance, rel):
        """
        Check that the current user has the permissions required to delete the
        current object.
        """
        assert type(rel) == str, "'rel' must be a string object"
        assert rel in ['song','album'], "'rel' must be 'song' or 'album'"

        if not hasattr(instance, rel):
            raise Exception("Could not find the contribution's '{}'".format(rel))
        content = getattr(instance, rel)

        # define variables
        contributor = instance.artist
        uploader = content.uploaded_by

        if not (artist == uploader or artist == contributor):
            raise ForbiddenError("You cannot delete this contribution")

        return True

    def check_tagging_permissions(self, artist, instance):
        """
        Ensures that the person editing the tag(s) is either the artist who
        uploaded the song/album, or the uploader allows contributors to edit
        tags.
        """
        uploader = instance.uploaded_by
        if uploader != artist:
            if not uploader.artist_profile.allow_contributors_to_edit_tags:
                raise ForbiddenError(f"You cannot add/remove tags from {instance.__str__()}")

    def _get_album_contributions(self, artist, *args, **kwargs):
        """
        Gets a list of albums that the current artist contributed to but did
        not upload.
        """
        # get all the contributions to albums that aren't uploaded by this artist
        contrib_albums = Album.hidden_objects \
            .filter(album_to_artist__primary_artist=False, contributors=artist) \
            .distinct()

        return contrib_albums

    def _get_song_contributions(self, artist, *args, **kwargs):
        """
        Gets a lit of songs that the current artist contributed to but did not
        upload.
        """
        contrib_songs = Song.hidden_objects \
            .filter(song_to_artist__primary_artist=False, contributors=artist) \
            .distinct()

        return contrib_songs

    def _get_album_metrics(self, serializer, artist, *args, **kwargs):
        # send an empty list if there is no data anyway
        if len(serializer.data) == 0:
            return []

        data = serializer.data
        env = 'test' if settings.DEBUG else 'production'

        # attach the data to the serializer data
        for album in serializer.data:
            album_object = Album.objects.get(id=album['album_id'])
            is_uploader = artist == album_object.uploaded_by

            # only send back metrics if the user is the uploading artist
            # or the contributor is allowed to see metrics
            if is_uploader or album_object.uploaded_by.artist_profile.share_data_with_contributors:
                album['total_streams'] = album_object.number_of_streams

            # create dict with more advanced metrics info
            # only send if user is uploading artist or artist allows advanced
            # data sharing
            if is_uploader or album_object.uploaded_by.artist_profile.share_advanced_data_with_contributors:
                advanced_metrics = {}
                # calculate metrics
                album['advanced_metrics'] = advanced_metrics

        return data

    def _get_song_metrics(self, serializer, artist, *args, **kwargs):
        # send an empty list if there is no data anyway
        if len(serializer.data) == 0:
            return []

        data = serializer.data

        for song in serializer.data:
            song_object = Song.objects.get(id=song['song_id'])
            is_uploader = artist == song_object.uploaded_by

            # only send back metrics if the user is the uploading artist
            # or the contributor is allowed to see the metrics
            if is_uploader or song_object.uploaded_by.artist_profile.share_data_with_contributors:
                song['total_streams'] = song_object.number_of_streams

            # create dict with more advanced metrics info
            # only send if user is uploading artist or artist allows advanced
            # data sharing
            if is_uploader or song_object.uploaded_by.artist_profile.share_advanced_data_with_contributors:
                # calculate metrics...
                song['advanced_metrics'] = calculate_advanced_song_analytics(song_object)

        return data

    @action(detail=False, methods=['get','post','patch','delete'])
    @notifier(
        trigger='album-upload',
        methods=['post'], album=True, 
        force=True, medium='email', artist=True, check_first=True
    )
    @notifier(
        trigger='album-edit',
        methods=['patch'], album=True,
        force=True, medium='email', artist=True, check_first=True
    )
    @attributor(name="Upload Album", methods=['post'])
    def albums(self, request, *args, **kwargs):
        """
        """
        # get the current artist
        artist = self.get_current_artist(request)

        album_queryset = self.platform.HiddenAlbums.filter(uploaded_by=artist)
        kwargs['context'] = self.get_serializer_context()
        if request.method in ['PATCH','DELETE']:
            try:
                album_id = request.data.pop('album_id')
            except AttributeError:
                _mutable = request.data._mutable
                request.data._mutable = True
                album_id = request.data.pop('album_id')
                request.data._mutable = _mutable
            assert album_id, "could not get an album ID"
            if type(album_id) == list:
                album_id = album_id[0]
            assert type(album_id) == str, f"album_id is not a string, got type {type(album_id)}"

        if request.method == 'GET':
            albums = album_queryset
            serializer = content_ser_v1.AlbumSerializer(albums, many=True)

            # attach the number of streams
            metrics_data = self._get_album_metrics(serializer, artist, *args, **kwargs)
            return responses.OK(data=metrics_data)

        elif request.method == 'POST':
            # default album platform to 'Revibe'
            if 'platform' not in request.data.keys():
                try:
                    _mutable = request.data._mutable
                    request.data._mutable = True
                    request.data['platform'] = str(self.platform)
                    request.data._mutable = _mutable
                except TypeError as e:
                    return responses.PROGRAM_ERROR()

            serializer = content_ser_v1.AlbumSerializer(data=request.data, *args, **kwargs)
            if serializer.is_valid():
                serializer.save()
                return responses.CREATED(serializer)
            else:
                return responses.SERIALIZER_ERROR_RESPONSE(serializer)
            return responses.DEFAULT_400_RESPONSE()

        elif request.method == 'PATCH':
            try:
                instance = Album.objects.get(id=album_id)

                # ensure editing artist is the uploading artist
                if artist != instance.uploaded_by:
                    return responses.NOT_PERMITTED(detail="you are not permitted to edit this album")

                serializer = content_ser_v1.AlbumSerializer(data=request.data, instance=instance, partial=True, *args, **kwargs)
                if serializer.is_valid():
                    serializer.save()
                    return responses.UPDATED(serializer=serializer)
                else:
                    return responses.SERIALIZER_ERROR_RESPONSE(serializer)
                return responses.DEFAULT_400_RESPONSE()
            except Exception as e:
                return responses.PROGRAM_ERROR(detail=str(e))

        elif request.method == 'DELETE':
            instance = Album.objects.get(pk=album_id)

            # ensure editing artist is the uploading artist
            if artist != instance.uploaded_by:
                raise ForbiddenError("You are not permitted to delete this album")

            # set the album to 'is_deleted'
            instance.delete()
            return responses.DELETED()

        else:
            return responses.NO_REQUEST_TYPE()

    @action(detail=False, methods=['post'], url_path=r"albums/(?P<album_id>[a-zA-Z0-9-_]+)/post", url_name="album_post-upload")
    def album_post_upload(self, request, album_id=None, *args, **kwargs):
        artist = self.get_current_artist(request)
        try:
            album = Album.hidden_objects.get(id=album_id)
        except Album.DoesNotExist:
            raise network.NotFoundError()

        raise NotImplementedError()

    @action(detail=False, methods=['get','post','patch','delete'])
    def songs(self, request, *args, **kwargs):
        artist = self.get_current_artist(request)

        song_queryset = self.platform.HiddenSongs.filter(uploaded_by=artist)
        album_queryset = self.platform.HiddenAlbums.filter(uploaded_by=artist)
        kwargs['context'] = self.get_serializer_context()
        if request.method in ['PATCH','DELETE']:
            try:
                song_id = request.data.pop('song_id')
            except AttributeError:
                _mutable = request.data._mutable
                request.data._mutable = True
                song_id = request.data.pop('song_id')
                request.data._mutable = _mutable
            assert song_id, "could not get a song ID"
            if type(song_id) == list:
                song_id = song_id[0]
            assert type(song_id) == str, f"song_id is not a string, got type {type(album_id)}"

        if request.method == 'GET':
            songs = song_queryset

            params = request.query_params
            if 'album_id' in params.keys():
                songs = songs.filter(album=album_queryset.get(pk=params['album_id']))

            # get the serialized data
            serializer = content_ser_v1.SongSerializer(songs, many=True)

            # attach the number of streams
            metrics_data = self._get_song_metrics(serializer, artist, *args, **kwargs)
            return responses.OK(data=metrics_data)


        elif request.method == 'POST':
            try:
                # set 'Revibe' as the default platform
                if 'platform' not in request.data.keys():
                    _mutable = request.data._mutable
                    request.data._mutable = True
                    request.data['platform'] = str(self.platform)
                    request.data._mutable = _mutable

                serializer = content_ser_v1.SongSerializer(data=request.data, *args, **kwargs)
                if not serializer.is_valid():
                    return responses.SERIALIZER_ERROR_RESPONSE(serializer=serializer)

                song = serializer.save()

                # send Kayne an email with newly uploaded songs
                try:
                    to_send_mail = retrieve_variable('kayne-send-email-on-song-upload', False, is_bool=True)
                    if to_send_mail:
                        send_mail(
                            subject="Song Upload Notification",
                            message=f"New song uploaded.\nSong '{song.title}' uploaded by {artist.name} at {datetime.datetime.now()}.",
                            recipient_list=[retrieve_variable("kayne-song-upload-email-address", "kaynelynn@revibe.tech", output_type=str),],
                            from_email='"Revibe System Notification" <noreply@revibe.tech>',
                            fail_silently=True
                        )
                except Exception:
                    pass

                return responses.CREATED(serializer=serializer)
            except Exception as e:
                if isinstance(e, APIException):
                    raise e
                else:
                    # send Jordan an email with the issue
                    send_mail(
                        subject="Upload song error",
                        message=f"Error uploading song. \n\nError: {str(e)} \n\nDatetime: {datetime.datetime.now()} \n\nArtist: {artist.name}",
                        from_email='"Song Upload Error" <noreply@revibe.tech>',
                        recipient_list=["jordanprechac@revibe.tech",],
                        fail_silently=True
                    )
                    return responses.PROGRAM_ERROR(str(e))

        elif request.method == 'PATCH':
            instance = Song.objects.get(pk=song_id)

            # ensure this artist uploaded this song
            if artist != instance.uploaded_by:
                raise ForbiddenError("You are not authorized to edit this song")

            serializer = content_ser_v1.SongSerializer(data=request.data, instance=instance, partial=True, *args, **kwargs)
            if serializer.is_valid():
                serializer.save()
                return responses.UPDATED(serializer=serializer)

            return responses.SERIALIZER_ERROR_RESPONSE(serializer)

        elif request.method == 'DELETE':
            instance = Song.objects.get(pk=song_id)

            # ensure this artist uploaded this song
            if artist != instance.uploaded_by:
                raise ForbiddenError("You are not authorized to delete this song")

            instance.delete()
            return responses.DELETED()

        return responses.NO_REQUEST_TYPE()

    @action(detail=False)
    def contributions(self, request):
        artist = self.get_current_artist(request)

        songs = self.platform.HiddenSongContributors.filter(artist=artist, primary_artist=False)
        albums = self.platform.HiddenAlbumContributions.filter(artist=artist, primary_artist=False, album__is_displayed=True)
        song_serializer = content_ser_v1.SongContributorSerializer(songs, many=True)
        album_serializer = content_ser_v1.AlbumContributorSerializer(albums, many=True)
        return Response({
            'songs': song_serializer.data,
            'albums': album_serializer.data
        })

    @action(detail=False, methods=['get','post','patch','delete'], url_path='contributions/albums', url_name="album_contributions")
    @notifier(
        trigger='inverse-new-contribution', user_target='data.artist_id.artist_user',
        methods=['post'], album=True,
        force=True, medium='email', artist=True, check_first=True
    )
    @notifier(
        trigger='new-contribution',
        methods=['post'], album=True,
        force=True, medium='email', artist=True, check_first=True
    )
    @attributor(name="Add Contributor", methods=['post'])
    @attributor(name="Invite Contributor", methods=['post'])
    def album_contributions(self, request, *args, **kwargs):
        artist = self.get_current_artist(request)

        albumcontribution_queryset = self.platform.HiddenAlbumContributions.filter(artist=artist, primary_artist=False)
        kwargs['context'] = self.get_serializer_context()
        if request.method in ['PATCH','DELETE']:
            contribution_id = request.data['contribution_id']

        if request.method == 'GET':
            # # old, but keeping here for reference
            # contrib_albums = AlbumContributor.objects.filter(primary_artist=False, artist=artist)
            # albums = list(set([ac.album for ac in contrib_albums if ac.album.is_deleted == False]))

            albums = self._get_album_contributions(artist, *args, **kwargs)
            album_serializer = content_ser_v1.AlbumSerializer(albums, many=True)

            # attach metrics when running in the cloud
            metrics_data = self._get_album_metrics(album_serializer, artist, *args, **kwargs)
            return responses.OK(data=metrics_data)

        elif request.method == 'POST':
            # ensure that it's not a placeholder contribution
            if request.data.get('placeholder', False) == True:
                create_placeholder(request.data)
                return responses.CREATED()

            # do the normal thing
            serializer = content_ser_v1.AlbumContributorSerializer(data=request.data, *args, **kwargs)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            else:
                return responses.SERIALIZER_ERROR_RESPONSE(serializer)
            return responses.DEFAULT_400_RESPONSE()

        elif request.method == 'PATCH':
            instance = AlbumContributor.objects.get(pk=contribution_id)

            # check permissions and settings
            self.check_contrib_permissions(artist, instance, 'album')

            # perform update
            serializer = content_ser_v1.AlbumContributorSerializer(data=request.data, instance=instance, partial=True, *args, **kwargs)
            if serializer.is_valid():
                serializer.save()
                return responses.OK(serializer=serializer)

            return responses.SERIALIZER_ERROR_RESPONSE(serializer)

        elif request.method == 'DELETE':
            instance = AlbumContributor.objects.get(pk=contribution_id)

            # check permissions
            self.check_delete_permissions(artist, instance, 'album')

            instance.delete()
            return responses.DELETED()

        else:
            return responses.NO_REQUEST_TYPE()

    @action(detail=False, methods=['get','post','patch','delete'], url_path='contributions/songs', url_name="song_contributions")
    @notifier(
        trigger='inverse-new-contribution', user_target="data.artist_id.artist_user",
        methods=['post'], song=True,
        force=True, medium='email', artist=True, check_first=True
    )
    @notifier(
        trigger='new-contribution',
        methods=['post'], song=True,
        force=True, medium='email', artist=True, check_first=True
    )
    @attributor(name="Add Contributor", methods=['post'])
    @attributor(name="Invite Contributor", methods=['post'])
    def song_contributions(self, request, *args, **kwargs):
        artist = self.get_current_artist(request)

        songcontribution_queryset = self.platform.HiddenSongContributors.filter(artist=artist, primary_artist=False)
        full_queryset = SongContributor.objects.all()
        kwargs['context'] = self.get_serializer_context()
        if request.method in ['PATCH','DELETE']:
            contribution_id = request.data.pop('contribution_id')

        if request.method == 'GET':
            # # deprecated, kept here for reference
            # contrib_songs = SongContributor.objects.filter(primary_artist=False, artist=artist)
            # songs = list(set([sc.song for sc in contrib_songs if sc.song.is_deleted==False]))

            songs = self._get_song_contributions(artist)
            song_serializer = content_ser_v1.SongSerializer(songs, many=True, *args, **kwargs)

            # attach stream data if in the cloud
            metrics_data = self._get_song_metrics(song_serializer, artist, *args, **kwargs)
            return responses.OK(data=metrics_data)

        elif request.method == 'POST':
            # ensure that it's not a placeholder contribution
            if request.data.get('placeholder', False) == True:
                create_placeholder(request.data)
                return responses.CREATED()

            # do the normal thing
            serializer = content_ser_v1.SongContributorSerializer(data=request.data, *args, **kwargs)
            if serializer.is_valid():
                serializer.save()
                return responses.CREATED(serializer)
            else:
                return responses.SERIALIZER_ERROR_RESPONSE(serializer)
            return responses.DEFAULT_400_RESPONSE()

        elif request.method == 'PATCH':
            instance = SongContributor.objects.get(pk=contribution_id)

            # check permissions and settings
            self.check_contrib_permissions(artist, instance, 'song')

            serializer = content_ser_v1.SongContributorSerializer(instance=instance, data=request.data, partial=True, *args, **kwargs)
            if serializer.is_valid():
                serializer.save()
                return responses.UPDATED(serializer=serializer)

            return responses.SERIALIZER_ERROR_RESPONSE(serializer)

        elif request.method == 'DELETE':
            instance = SongContributor.objects.get(pk=contribution_id)

            # check permissions
            self.check_delete_permissions(artist, instance, 'song')

            instance.delete()
            return responses.DELETED()

        else:
            return responses.NO_REQUEST_TYPE()

    @action(detail=False, methods=['post'], url_path="contributions/approve")
    @notifier(
        trigger="approve-contribution",
        contribution=True,
        medium='email', artist=True, check_first=True
    )
    @notifier(
        trigger="approve-contribution-inverse", user_target="data.song_id.uploaded_by.artist_user",
        contribution=True,
        force=True, medium='email', artist=True,
    )
    @notifier(
        trigger="approve-contribution-inverse", user_target="data.album_id.uploaded_by.artist_user",
        contribution=True,
        force=True, medium='email', artist=True
    )
    def approve_contribution(self, request, *args, **kwargs):
        """
        Approves or denies song and album contributions.
        """
        artist = self.get_current_artist(request)

        # validate data
        required_fields = ['content','contribution_id','action']
        for field in required_fields:
            if field not in request.data.keys():
                return responses.SERIALIZER_ERROR_RESPONSE(detail="{} must be included in request data".format(field))
        if request.data['action'].lower() not in ['approve','deny']:
            return responses.SERIALIZER_ERROR_RESPONSE(detail="'action' must be either 'approve' or 'deny'")
        approval = True if request.data['action'].lower() == 'approve' else False

        if request.data['content'] == 'song':
            model = SongContributor
            serializer = content_ser_v1.SongContributorSerializer
        elif request.data['content'] == 'album':
            model = AlbumContributor
            serializer = content_ser_v1.AlbumContributorSerializer
        else:
            return responses.SERIALIZER_ERROR_RESPONSE(detail="Field 'content' must be either 'song' or 'album'.")

        # get contribution and check request user against contribution artist
        contribution = model.objects.get(pk=request.data['contribution_id'])
        if not artist == contribution.artist:
            return responses.NOT_PERMITTED(detail="You are not authorized to approve this contribution")

        # set instance data
        contribution.pending = False
        contribution.approved = approval
        contribution.save()

        return responses.UPDATED(serializer(instance=contribution))


    # register social media
    @action(detail=False, methods=['post', 'patch', 'delete'], url_path="social-media", url_name="social_media")
    @attributor(name="Add Relink", methods=['post'])
    def register_social_media(self, request, *args, **kwargs):
        """
        Adds, edits, or removes a social media link from an artist's profile
        """
        artist = self.get_current_artist(request)
        kwargs['context'] = self.get_serializer_context()

        if request.method in ['PATCH', 'DELETE'] and request.data.get('socialmedia_id', None) == None:
            raise ExpectationFailedError(detail="'socialmedia_id' must be included in request fields")

        if request.method == 'POST':
            # validate data
            errors = []
            if 'service' not in request.data.keys():
                errors['service'] = ["'service' must be included in data fields"]
            if 'handle' not in request.data.keys():
                errors['handle'] = ["'handle' must be included in data fields"]
            desc = getattr(request.data, 'description', False)
            if request.data['service'] == 'other' and desc != False:
                errors['description'] = ["if 'service' is 'other', must include 'description' field"]
                errors['service'].append("if 'service' is 'other', must include 'description' field")
            # return errors if there are any
            if len(errors) > 0:
                raise ExpectationFailedError(detail=errors)

            # continue with request...
            context = self.get_serializer_context()
            serializer = SocialMediaSerializer(data=request.data, *args, **kwargs)
            if not serializer.is_valid():
                return responses.SERIALIZER_ERROR_RESPONSE(serializer=serializer)

            serializer.save()
            return responses.CREATED(serializer=serializer)

        elif request.method == 'PATCH':
            media_id = request.data.get('socialmedia_id')
            instance = SocialMedia.objects.get(id=media_id)

            if artist.artist_profile != instance.artist_profile:
                raise ForbiddenError("You cannot edit this linked account")

            kwargs['context'] = self.get_serializer_context()
            serializer = SocialMediaSerializer(instance=instance, data=request.data, *args, **kwargs)
            if not serializer.is_valid():
                raise ExpectationFailedError(detail=serializer.errors)

            serializer.save()
            
            return responses.OK(serializer=serializer)

        elif request.method == 'DELETE':
            social_media = SocialMedia.objects.get(id=request.data['socialmedia_id'])

            if artist.artist_profile != social_media.artist_profile:
                raise ForbiddenError("You cannot remove this linked social media")

            social_media.delete()

            return responses.DELETED()

        else:
            return responses.NO_REQUEST_TYPE()

    # genre & tag content
    @action(detail=False, methods=['post', 'delete'], url_path=r"songs/(?P<song_id>[a-zA-Z0-9-_]+)/tags", url_name="tag-song")
    def tag_song(self, request, song_id=None, *args, **kwargs):
        # stuff for all requests
        artist = self.get_current_artist(request)
        song = Song.objects.get(id=song_id)

        if request.method == 'POST':
            # check that the artist can add taqs to a song
            self.check_tagging_permissions(artist, song)

            # add the tags to the song
            tags = [str(x) for x in request.data['tags']]
            add_tag_to_song(tags, song)

            return responses.CREATED()

        elif request.method == 'DELETE':
            # check that the artist can remove tags from a song
            self.check_tagging_permissions(artist, song)

            # remove the tags from the song
            tags = [str(x) for x in request.data['tags']]
            remove_tag_from_song(tags, song)

            return responses.DELETED()

    @action(detail=False, methods=['post', 'delete'], url_path=r"albums/(?P<album_id>[a-zA-Z0-9-_]+)/tags", url_name="tag-album")
    def tag_album(self, request, album_id=None, *args, **kwargs):
        # stuff for all request
        artist = self.get_current_artist(request)
        album = Album.objects.get(id=album_id)

        if request.method == 'POST':
            # check that the artist can add tags to the album
            self.check_tagging_permissions(artist, album)

            # add the tags to the album
            tags = [str(x) for x in request.data['tags']]
            add_tag_to_album(tags, album)

            return responses.CREATED()

        elif request.method == 'DELETE':
            # check that the artist can remove tags from an album
            self.check_tagging_permissions(artist, album)

            # remove the tags from the album
            tags = [str(x) for x in request.data['tags']]
            remove_tag_from_album(tags, album)

            return responses.DELETED()

    @action(detail=False, methods=['post', 'delete'], url_path=r"songs/(?P<song_id>[a-zA-Z0-9-_]+)/genres", url_name="genre-song")
    def genre_song(self, request, song_id=None, *args, **kwargs):
        # stuff for all requests
        artist = self.get_current_artist(request)
        song = Song.objects.get(id=song_id)

        if request.method == 'POST':
            # check that the artist can add genres to a song
            self.check_tagging_permissions(artist, song)
            
            # add the genres to the song
            genres = [str(x) for x in request.data['genres']]
            add_genres_to_object(genres, song)

            return responses.CREATED()
        
        elif request.method == 'DELETE':
            # check that the artist can remove genres
            self.check_tagging_permissions(artist, song)

            # remove the genres
            genres = [str(x) for x in request.data['genres']]
            remove_genres_from_object(genres, song)

            return responses.DELETED()

    @action(detail=False, methods=['post','delete'], url_path=r"albums/(?P<album_id>[a-zA-Z0-9-_]+)/genres", url_name="genre-album")
    def genre_album(self, request, album_id=None, *args, **kwargs):
        # stuff for all requests
        artist = self.get_current_artist(request)
        album = Album.objects.get(id=album_id)

        if request.method == 'POST':
            # check that the artist can add genres
            self.check_tagging_permissions(artist, album)

            # add the genres
            genres = [str(x) for x in request.data['genres']]
            add_genres_to_object(genres, album)

            return responses.CREATED()
        
        elif request.method == 'DELETE':
            # check that the artist can remove genres
            self.check_tagging_permissions(artist, album)

            # add the genres
            genres = [str(x) for x in request.data['genres']]
            remove_genres_from_object(genres, album)

            return responses.DELETED()


class ArtistAnalyticsViewSet(GenericPlatformViewSet):
    """
    Contains the endpoints for the Artist Portal Dashboards
    """
    platform = "revibe"
    permission_classes = [TokenOrSessionAuthentication]
    required_alternate_scopes = {
        "GET": [["ADMIN"], ["first-party", "artist"]]
    }

    def initial(self, request, *args, **kwargs):
        whatever = super().initial(request, *args, **kwargs)

        self.artist = get_authenticated_artist(request)

        return whatever

    def list(self, request, *args, **kwargs):
        pass
        # page = analytics.dashboard.full_dashboard()

        # return responses.OK(data=page)
    
    @action(detail=False, methods=['get'], url_path=r"(?P<endpoint>[a-zA-Z0-9-]+)", url_name="charts")
    def analytics_endpoint(self, request, endpoint=None, *args, **kwargs):
        # get optional param values
        params = request.query_params
        type_ = get_url_param(params, 'type')

        possible_extras = ['time_period', 'time_interval', ('num_bars', int), ('distinct', bool)]
        get_param = lambda key : get_url_param(params, key) if isinstance(key, str) else get_url_param(params, key[0], type_=key[1])
        extras = {(key if isinstance(key, str) else key[0]): get_param(key) for key in possible_extras}

        # get the chart class
        stripped_endpoint = endpoint.split('-')[0].split('_')[0]
        endpoints = {
            "bar": BarChart,
            "card": CardChart,
            "line": LineChart
        }
        chart_class = endpoints.get(stripped_endpoint, None)
        if chart_class == None:
            raise network.BadRequestError(f"Could not find a chart type from '{endpoint}'")

        # get the chart data
        chart = chart_class(artist=self.artist, type_=type_, **extras)

        # return the stuff
        return responses.OK(data=chart.data)


class UserViewSet(viewsets.GenericViewSet):
    serializer_class = UserSerializer
    permission_classes = [TokenOrSessionAuthentication]
    required_alternate_scopes = {
        'GET': [['ADMIN'],['first-party']],
        'POST': [['ADMIN'],['first-party']],
        'PATCH': [['ADMIN'],['first-party']],
        'PUT': [['ADMIN'],['first-party']],
        'DELETE': [['ADMIN'],['first-party']],
    }

    def list(self, request, *args, **kwargs):
        return Response(UserSerializer(request.user, context=self.get_serializer_context()).data)

    def patch(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = request.user
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        if serializer.is_valid():
            serializer.save()
            return responses.UPDATED(serializer)
        else:
            return responses.SERIALIZER_ERROR_RESPONSE(serializer)
        return responses.DEFAULT_400_RESPONSE()

    @action(detail=False, methods=['post'], url_path="change-password", url_name="change-password")
    @notifier(
        trigger="change-password",
        force=True, medium='email',
    )
    def change_password(self, request, *args, **kwargs):
        user = request.user

        try:
            change_password(user, **dict(request.data))
        except PasswordValidationError as e:
            raise network.BadRequestError(str(e))

        return responses.UPDATED()


@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def view_reset_password(request, *args, **kwargs):
    user_email = reset_password(**dict(request.data))

    return responses.OK(data={"email": str(user_email)})

