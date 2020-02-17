from django.conf import settings
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
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from rest_auth.registration.views import SocialConnectView
from oauth2_provider.views import TokenView, RevokeTokenView
from oauth2_provider.contrib.rest_framework import TokenHasReadWriteScope,TokenMatchesOASRequirements, TokenHasScope
from oauth2_provider.models import Application, AccessToken, RefreshToken
from oauthlib import common
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
from revibe.utils.params import get_url_param
from revibe._errors import accounts ,network
from revibe._errors.accounts import AccountNotFound, NotArtistError
from revibe._errors.network import ConflictError, ForbiddenError, NotImplementedError, ExpectationFailedError
from revibe._helpers import responses, const

from accounts.permissions import TokenOrSessionAuthentication
from accounts.models import *
from accounts.serializers.v1 import *
from accounts._helpers import validation
from administration.models import Campaign
from content.models import Album, Song, SongContributor, AlbumContributor
from content.serializers import v1 as content_ser_v1
from content.utils.models import add_tag_to_song, remove_tag_from_song
from metrics.models import Stream
from music.models import *
from music.serializers import v1 as music_ser_v1

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

class AuthenticationViewSet(viewsets.GenericViewSet):
    queryset = CustomUser.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.AllowAny]

    def __init__(self, *args, **kwargs):
        super(AuthenticationViewSet, self).__init__(*args, **kwargs)
        self.application = Application.objects.get(name=const.FIRST_PARTY_APPLICATION_NAME)

    # helper functions
    def get_device(self, data):
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

    def create_libraries(self, user):
        """
        Creates default libraries when creating an account, Revibe and YouTube
        """
        logger.info("Creating default libraries...")
        assert isinstance(user, CustomUser), "must pass a user to 'create_libraries()'"
        default_libraries = [const.REVIBE_STRING, const.YOUTUBE_STRING]
        for def_lib in default_libraries:
            Library.objects.create(platform=def_lib, user=user)

        # check that it worked
        num_created = len(Library.objects.filter(user=user))
        if num_created < len(default_libraries):
            logger.error("Error creating libraries: only created {}, should have created {}.".format(num_created, len(default_libraries)))
            raise ValidationError("Error creating libraries")

    def revoke_tokens(self, device=None, user=None, all=False, *args, **kwargs):
        logger.info("Revoking old tokens...")
        assert bool(device) != bool(user), "can only pass a user or a device" # functions as an XOR operator
        if device:
            tokens = AccessToken.objects.filter(token_device=device)
            for at in tokens:
                at.source_refresh_token.delete()
                at.delete()
        elif user:
            pass

    def get_expire_time(self, device, *args, **kwargs):
        time = const.BROWSER_EXPIRY_TIME if device.device_type == 'browser' else const.DEFAULT_EXPIRY_TIME
        return timezone.now() + datetime.timedelta(hours=time)

    def get_scopes(self, device, user, *args, **kwargs):
        scopes = ["first-party"]
        if device.device_type == 'browser':
            scopes.append('artist')
        if user.is_staff:
            scopes.append("ADMIN")
        return " ".join(scopes)

    def generate_tokens(self, device, user, *args, **kwargs):
        logger.info("Generating tokens...")
        access_token = AccessToken(
            user=user,
            token=common.generate_token(),
            application=self.application,
            scope=self.get_scopes(device),
            expires=self.get_expire_time(device)
        )
        refresh_token = RefreshToken(
            user=user,
            token=common.generate_token(),
            application=self.application,
            access_token=access_token
        )

        access_token.save()
        refresh_token.save()

        access_token.source_refresh_token = refresh_token
        access_token.save()

        device.token = access_token
        device.save()

        logger.info("Tokens successfully created!")
        return access_token, refresh_token

    def set_cookies(self, response, access_token):
        response.set_cookie(const.ACCESS_TOKEN_COOKIE_NAME, access_token.token, samesite=None, path="/")
        return response

    # remove all potential default functions
    def list(self, request, *args, **kwargs):
        return responses.NOT_IMPLEMENTED()
    def retrieve(self, request, *args, **kwargs):
        return responss.NOT_IMPLEMENTED()
    def create(self ,request, *args, **kwargs):
        return responses.NOT_IMPLEMENTED()
    def update(self, request, *args, **kwargs):
        return responses.NOT_IMPLEMENTED()
    def destroy(self, request, *args, **kwargs):
        return responses.NOT_IMPLEMENTED()

    @action(detail=False, methods='post')
    def login(self, request, *args, **kwargs):
        login_data = {
            "username": request.data['username'],
            "password": request.data['password'],
        }
        kwargs['context'] = self.get_serializer_context()
        serializer = LoginAccountSerializer(data=login_data)
        if serializer.is_valid():

            device = get_device(request.data)
            self.revoke_tokens(device=device)

            # prepare token fields
            user = serializer.validated_data
            expire = self.get_expire_time(device)
            scope = self.get_scopes(device, user)

            # create tokens
            access_token, refresh_token = self.generate_tokens(device, user, *args, **kwargs)

            data = {
                "user": UserSerializer(user, context=self.get_serializer_context()).data,
                "access_token": access_token.token,
            }
            if device.device_type != 'browser':
                data.update({"refresh_token": refresh_token.token})

            return Response(data, status=status.HTTP_200_OK)

        else:
            return responses.SERIALIZER_ERROR_RESPONSE(serializer)

        return responses.DEFAULT_400_RESPONSE()

    @action(detail=False, methods=['post'], url_path='refresh-token')
    def refresh_token(self, request, *args, **kwargs):
        refresh_token = RefreshToken.objects.get(token=request.data['refresh_token'])
        access_token = refresh_token.access_token

        access_token.token = common.generate_token()

        access_token.expires = self.get_expire_time(access_token.token_device)

        access_token.save()

        return Response({"access_token": access_token.token}, status=status.HTTP_200_OK)

    @action(detail=False, methods=['post'])
    def logout(self, request, *args, **kwargs):
        token = AccessToken.objects.get(token=request.data['access_token'])

        # send back an issue if server could not find the user
        if not token.user:
            return responses.UNAUTHORIZED(detail="could not identify the current user")
        elif token.user != request.user:
            return responses.NOT_PERMITTED(detail="could not identify the current user as the owner of this token")

        if token.token_device:
            token.token_device.delete()

        token.refresh_token.delete()
        token.delete()

        return responses.OK(detail="logout successful")

    @action(detail=False, methods=['post'], url_path='logout-all')
    def logout_all(self, request, *args, **kwargs):
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

class RegistrationAPI(generics.GenericAPIView):
    """
    this works when application has following attributes:
    client type: confidential
    Authorization grant type: Resource owner password-based
    curl -X POST -d "client_id=y2iPQuosC9qgIJZua9w5VCpHMTdO7Onkl2RF9qQk&client_secret=KE5IMAxQizJAwRKkKUY244PctidKPL88mQwyGPX6ci9ZymHsYSgxxTLeJNMppf1lerlNfjQnKYpZ1xzlsRFtdV6S9gLfb6WdFnVu29BSw8lteoqiU6ZoJtnxabs4slgs&grant_type=password&username=rileystephens&password=Reed1rile2" http://127.0.0.1:8000/o/token/
    """
    serializer_class = UserSerializer
    permission_classes = [permissions.AllowAny]

    def attach_referer(self, params, profile, *args, **kwargs):
        # check for marketing campaign
        cid = get_url_param(params, 'cid')
        if cid != None:
            try:
                campaign = Campaign.objects.get(uri=cid)
                profile.campaign = campaign
                profile.save()
            except Exception as e:
                pass

        # check for user referral
        uid = get_url_param(params, 'uid')
        if uid != None:
            try:
                referrer = CustomUser.objects.get(id=uid)
                profile.referrer = referrer
                profile.save()
            except Exception as e:
                raise e

        return profile

    def post(self, request, *args, **kwargs):
        # check expectations
        username = request.data['username']
        email = request.data.get('email', None)

        errors = {}
        # check if username already exists
        if not validation.check_username(username):
            errors['username'] = []
            err = f"Username '{username}' already exists.'"
            errors['username'].append(err)

        if email and (not validation.check_email(email)):
            errors['email'] = []
            err = f"A user with email '{email}' already exists."
            errors['email'].append(err)

        if errors != {}:
            raise ConflictError(detail=errors)

        # run registration
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():

            device = request.data['device_type']

            application = Application.objects.get(name="Revibe First Party Application")

            try:
                user=serializer.save()
            except IntegrityError as err:
                return responses.CONFLICT(detail=str(err))

            # check query params for referrals and/or marketing campaign
            params = request.query_params
            self.attach_referer(params, user.profile)

            time = const.BROWSER_EXPIRY_TIME if device == 'browser' else const.DEFAULT_EXPIRY_TIME
            expire = timezone.now() + datetime.timedelta(hours=time)

            scopes = ['first-party']
            if device == 'browser':
                scopes.append('artist')
            scope = " ".join(scopes)

            access_token = AccessToken(
                user=user,
                expires=expire,
                token=common.generate_token(),
                application=application,
                scope=scope
            )
            access_token.save()

            refresh_token = RefreshToken(
                user=user,
                token=common.generate_token(),
                application=application,
                access_token=access_token
            )
            refresh_token.save()

            access_token.source_refresh_token = refresh_token
            access_token.save()

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

class LoginAPI(generics.GenericAPIView):
    permission_classes = [permissions.AllowAny]
    serializer_class = LoginAccountSerializer

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super(LoginAPI, self).dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        login_data = {
            "username": request.data['username'],
            "password": request.data['password'],
        }
        serializer = self.get_serializer(data=login_data)
        if serializer.is_valid():

            device = request.data['device_type']

            user = serializer.validated_data

            scopes = ["first-party"]
            if device == 'browser':
                scopes.append('artist')
            if user.is_staff:
                scopes.append("ADMIN")
            scope = " ".join(scopes)

            tokens = AccessToken.objects.filter(user=user)
            for at in tokens:
                if at.scope == scope:
                    at.source_refresh_token.delete()
                    at.delete()

            application = Application.objects.get(name="Revibe First Party Application")

            time = const.BROWSER_EXPIRY_TIME if device == 'browser' else const.DEFAULT_EXPIRY_TIME
            expire = timezone.now() + datetime.timedelta(hours=time)

            access_token = AccessToken(
                user=user,
                expires=expire,
                token=common.generate_token(),
                application=application,
                scope=scope
            )
            access_token.save()

            refresh_token = RefreshToken(
                user=user,
                token=common.generate_token(),
                application=application,
                access_token=access_token
            )
            refresh_token.save()

            access_token.source_refresh_token = refresh_token
            access_token.save()

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
        refresh_token = RefreshToken.objects.get(token=request.data['refresh_token'])
        access_token = refresh_token.access_token

        access_token.token = common.generate_token()

        device = request.data['device_type']
        time = const.BROWSER_EXPIRY_TIME if device == 'browser' else const.DEFAULT_EXPIRY_TIME
        access_token.expires = timezone.now() + datetime.timedelta(hours=time)

        access_token.save()

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
            "register_link": self.register_link,
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


class SpotifyRefresh(generics.GenericAPIView):
    permission_classes = (TokenOrSessionAuthentication)
    required_alternate_scopes = {
        'GET': [['ADMIN'], ['first-party']],
        'POST': [['ADMIN'], ['first-party']]
    }
    serializer_class = RefreshTokenSerializer

    def post(self, request, *args, **kwargs):
        # should spotify refresh token be verified against user?
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
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

class SpotifyLogout(generics.GenericAPIView):
    permission_classes = (TokenOrSessionAuthentication)
    required_alternate_scopes = {
        'GET': [['ADMIN'], ['first-party']],
        'POST': [['ADMIN'], ['first-party']]
    }

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

# class UserLinkedAccounts(generics.GenericAPIView):
#     permission_classes = [permissions.IsAuthenticated, TokenHasReadWriteScope]
#     serializer_class = SocialTokenSerializer
#
#     def get(self, request, *args, **kwargs):
#         serializer = self.get_serializer(data=request.data)
#         serializer.is_valid(raise_exception=True)
#         data = serializer.validated_data
#         return Response(data, status=status.HTTP_200_OK)
#     #     # return Response({"error":"User has not logged into Spotify."},status=status.HTTP_400_BAD_REQUEST) # should probably return current tokens
#     #
#     #     # return Response(SocialTokenSerializer(request.user, context=self.get_serializer_context()).data)

# Artist Account API Views

class UserArtistViewSet(GenericPlatformViewSet):
    """
    Artist Portal ONLY
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

    def create(self, request, *args, **kwargs):
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

        # add contributions from urls
        params = request.query_params

        # song contributions
        if 'song_contrib' in params.keys():
            contribs = params['song_contrib'].split(',')
            for contrib in contribs:
                obj = SongContributor.objects.get(id=contrib)
                # TODO: add some check for like obj.allow_add_on_register or something
                obj.artist = artist
                obj.pending = True
                obj.approved = False
                obj.save()

        # album contributions
        if 'album_contrib' in params.keys():
            contribs = params['album_contrib'].split(',')
            for contrib in contribs:
                obj = AlbumContributor.objects.get(id=contrib)
                # TODO: add some check for like obj.allow_add_on_register or something
                obj.artist = artist
                obj.pending = True
                obj.approved = False
                obj.save()

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
                album['total_streams'] = 0
                for song in album_object.song_set.all():
                    album['total_streams'] += Stream.count(song.id, Stream.environment == env)

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
        env = 'test' if settings.DEBUG else 'production'

        for song in serializer.data:
            song_object = Song.objects.get(id=song['song_id'])
            is_uploader = artist == song_object.uploaded_by

            # only send back metrics if the user is the uploading artist
            # or the contributor is allowed to see the metrics
            if is_uploader or song_object.uploaded_by.artist_profile.share_data_with_contributors:
                song['total_streams'] = Stream.count(song['song_id'], Stream.environment == env)

            # create dict with more advanced metrics info
            # only send if user is uploading artist or artist allows advanced
            # data sharing
            if is_uploader or song_object.uploaded_by.artist_profile.share_advanced_data_with_contributors:
                advanced_metrics = {}
                # calculate metrics...
                song['advanced_metrics'] = advanced_metrics

        return data

    @action(detail=False, methods=['get','post','patch','delete'])
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

            # attach the number of streams in running in the cloud
            if settings.USE_S3:
                metrics_data = self._get_album_metrics(serializer, artist, *args, **kwargs)
                return responses.OK(data=metrics_data)

            return responses.OK(serializer)

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
            instance.is_deleted = True
            instance.is_displayed = False
            instance.save()

            # set all songs to 'is_deleted'
            for song in instance.song_set.all():
                song.is_deleted = True
                song.is_displayed = False
                song.save()

            return responses.DELETED()

        else:
            return responses.NO_REQUEST_TYPE()

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

            # attach the number of streams in running in the cloud
            if settings.USE_S3:
                metrics_data = self._get_song_metrics(serializer, artist, *args, **kwargs)
                return responses.OK(data=metrics_data)

            return Response(serializer.data)

        elif request.method == 'POST':
            if 'platform' not in request.data.keys():
                _mutable = request.data._mutable
                request.data._mutable = True
                request.data['platform'] = str(self.platform)
                request.data._mutable = _mutable
            serializer = content_ser_v1.SongSerializer(data=request.data, *args, **kwargs)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            else:
                return responses.SERIALIZER_ERROR_RESPONSE(serializer)
            return responses.DEFAULT_400_RESPONSE()

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

            instance.is_deleted = True
            instance.is_displayed = False
            instance.save()
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
            if settings.USE_S3:
                metrics_data = self._get_album_metrics(album_serializer, artist, *args, **kwargs)
                return responses.OK(data=metrics_data)

            return responses.OK(serializer=album_serializer)

        elif request.method == 'POST':
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

    @action(detail=False, url_path='contributions/songs', methods=['get','post','patch','delete'], url_name="song_contributions")
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
            if settings.USE_S3:
                metrics_data = self._get_song_metrics(song_serializer, artist, *args, **kwargs)

                return responses.OK(data=metrics_data)

            return responses.OK(serializer=song_serializer)

        elif request.method == 'POST':
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

    @action(detail=False, url_path="contributions/approve", methods=['post'])
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


        artist = self.get_current_artist(request)

        if request.method == 'GET':
            raise NotImplementedError()

        return responses.NO_REQUEST_TYPE()

    # register social media
    @action(detail=False, url_path="social-media", methods=['post', 'patch', 'delete'])
    def register_social_media(self, request, *args, **kwargs):
        """
        Adds, edits, or removes a social media link from an artist's profile
        """
        artist = self.get_current_artist(request)
        kwargs['context'] = self.get_serializer_context()

        if request.method in ['PATCH', 'DELETE'] and getattr(request.data, 'socialmedia_id', None) == None:
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
            pass

        elif request.method == 'DELETE':
            pass

        return responses.NO_REQUEST_TYPE()

    # tag content
    @action(detail=False, methods=['post', 'delete'], url_path="songs/tags", url_name="tag_song")
    def tag_song(self, request, *args, **kwargs):
        # stuff for all requests
        artist = self.get_current_artist(request)
        song = Song.objects.get(id=request.data['song_id'])

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

class UserViewSet(generics.GenericAPIView):
    serializer_class = UserSerializer
    permission_classes = [TokenOrSessionAuthentication]
    required_alternate_scopes = {
        'GET': [['ADMIN'],['first-party']],
        'POST': [['ADMIN'],['first-party']],
        'PATCH': [['ADMIN'],['first-party']],
        'PUT': [['ADMIN'],['first-party']],
        'DELETE': [['ADMIN'],['first-party']],
    }

    def get(self, request, *args, **kwargs):
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
