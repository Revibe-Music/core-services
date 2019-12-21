from django.conf import settings
from django.core.exceptions import MultipleObjectsReturned, ObjectDoesNotExist
from django.http import HttpRequest
from django.utils import timesince
from rest_framework import viewsets, permissions, generics, status
from rest_framework.decorators import action
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
import requests
import json

from artist_portal.viewsets import GenericPlatformViewSet
from artist_portal._helpers import responses, const
from artist_portal._errors.random import ValidationError
from accounts.permissions import TokenOrSessionAuthentication
from accounts.models import *
from accounts.serializers.v1 import *
from content.models import Album, Song, SongContributor, AlbumContributor
from content.serializers import v1 as content_ser_v1
from music.serializers import v1 as music_ser_v1

class RegistrationAPI(generics.GenericAPIView):
    """
    this works when application has following attributes:
    client type: confidential
    Authorization grant type: Resource owner password-based
    curl -X POST -d "client_id=y2iPQuosC9qgIJZua9w5VCpHMTdO7Onkl2RF9qQk&client_secret=KE5IMAxQizJAwRKkKUY244PctidKPL88mQwyGPX6ci9ZymHsYSgxxTLeJNMppf1lerlNfjQnKYpZ1xzlsRFtdV6S9gLfb6WdFnVu29BSw8lteoqiU6ZoJtnxabs4slgs&grant_type=password&username=rileystephens&password=Reed1rile2" http://127.0.0.1:8000/o/token/
    """
    serializer_class = UserSerializer
    permission_classes = [permissions.AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            
            device = Device(
                device_id = request.data['device_id'],
                device_type = request.data['device_type'],
                device_name = request.data['device_name']
            )
            device.save()

            application = Application.objects.get(name="Revibe First Party Application")

            user=serializer.save()

            expire = timezone.now() + datetime.timedelta(days=2)

            scopes = ['first-party']
            if device.device_type == 'browser':
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
            device.token = access_token
            device.save()

            data = {
                "user": UserSerializer(user, context=self.get_serializer_context()).data,
            }

            response = Response(status=status.HTTP_200_OK)
            if device.device_type == 'browser':
                response.set_cookie(const.ACCESS_TOKEN_COOKIE_NAME, access_token.token)
                response.data = data
            else:
                data.update({
                    "access_token": access_token.token,
                    "refresh_token": refresh_token.token,
                })
                response.data = data
            return response

        else:
            return responses.SERIALIZER_ERROR_RESPONSE(serializer)
        return responses.DEFAULT_400_RESPONSE()

class LoginAPI(generics.GenericAPIView):
    permission_classes = [permissions.AllowAny]
    serializer_class = LoginAccountSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():

            try:
                device = Device.objects.get(device_id=request.data['device_id'],device_type=request.data['device_type'],device_name=request.data['device_name'])
            except (ObjectDoesNotExist):
                device = Device(
                    device_id = request.data['device_id'],
                    device_type = request.data['device_type'],
                    device_name = request.data['device_name']
                )
                device.save()
            except MultipleObjectsReturned:
                device = Device.objects.filter(device_id=request.data['device_id'],device_type=request.data['device_type'],device_name=request.data['device_name'])[0]
            except Exception as e:
                raise e
            
            tokens = AccessToken.objects.filter(token_device=device)
            for at in tokens:
                at.source_refresh_token.delete()
                at.delete()

            application = Application.objects.get(name="Revibe First Party Application")
            
            user = serializer.validated_data

            time = 5 if device.device_type == 'browser' else 2
            expire = timezone.now() + datetime.timedelta(hours=time)

            scopes = ["first-party"]
            if device.device_type == 'browser':
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
            device.token = access_token
            device.save()

            data = {
                "user": UserSerializer(user, context=self.get_serializer_context()).data,
            }

            response = Response(status=status.HTTP_200_OK)
            if device.device_type == 'browser':
                response.set_cookie(const.ACCESS_TOKEN_COOKIE_NAME, access_token.token)
                response.data = data
            else:
                data.update({
                    "access_token": access_token.token,
                    "refresh_token": refresh_token.token,
                })
                response.data = data
            return response
        
        else:
            return responses.SERIALIZER_ERROR_RESPONSE(serializer)
        
        return responses.DEFAULT_400_RESPONSE()


class RefreshTokenAPI(generics.GenericAPIView):
    permission_classes = [permissions.AllowAny]
    serializer_class = RefreshTokenSerializer

    def post(self, request, *args, **kwargs):
        refresh_token = RefreshToken.objects.get(token=request.data['refresh_token'])
        access_token = refresh_token.access_token

        access_token.token = common.generate_token()

        time = 5 if access_token.token_device.device_type == 'browser' else 2
        access_token.expires = access_token.expires + datetime.timedelta(hours=time)

        access_token.save()

        return Response({"access_token": access_token.token}, status=status.HTTP_200_OK)

class LogoutAPI(generics.GenericAPIView, RevokeTokenView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = AccessTokenSerializer

    def post(self, request, *args, **kwargs):
        token_location = request.data['access_token'] if ('access_token' in request.data.keys()) else request.COOKIES.get(const.ACCESS_TOKEN_COOKIE_NAME)
        token = AccessToken.objects.get(token=token_location)
        assert token.user == request.user, "Could not identify the current user"
        device = token.token_device # maybe token.device?

        token.refresh_token.delete()
        token.delete()
        device.delete()

        return Response({"detail": "logout successful"}, status=status.HTTP_200_OK)

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

class SpotifyConnect(SocialConnectView):
    """ Logs already authenticated user into Spotify account """
    adapter_class = SpotifyOAuth2Adapter
    callback_url = 'https://www.getpostman.com/oauth2/callback'
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

class UserArtistViewSet(GenericPlatformViewSet):
    """
    Artist Portal ONLY
    """
    platform = 'Revibe'
    queryset = CustomUser.objects.all()
    serializer_class = UserArtistSerializer
    permission_classes = [TokenOrSessionAuthentication]
    required_alternate_scopes = {
        'GET': [['ADMIN'],['first-party']],
        'POST': [['ADMIN'],['first-party']],
        'PATCH': [['ADMIN'],['first-party']],
        'PUT': [['ADMIN'],['first-party']],
        'DELETE': [['ADMIN'],['first-party']],
    }

    def list(self, request):
        if not request.user.artist:
            return Response({"detail": "could not identify the current user's artist profile"}, status=status.HTTP_401_UNAUTHORIZED)

        artist = self.serializer_class(request.user.artist, context=self.get_serializer_context()).data
        return Response(artist)

    def create(self, request, *args, **kwargs):
        kwargs['context'] = self.get_serializer_context()
        # check if user already has an artist object
        if request.user.artist != None:
            return Response({"detail": "this user already has an artist account"}, status=status.HTTP_409_CONFLICT)        
        
        # create the artist and attach to the user
        request.data['platform'] = 'Revibe'
        serializer = self.serializer_class(data=request.data, *args, **kwargs)
        if serializer.is_valid():
            artist = serializer.save()
            request.user.artist = artist
            request.user.is_artist = True
            request.user.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return responses.SERIALIZER_ERROR_RESPONSE(serializer)
        return responses.DEFAULT_400_RESPONSE()

    def patch(self, request, *args, **kwargs):
        instance = request.user.artist
        serializer = self.get_serializer(data=request.data, instance=instance, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        else:
            return responses.SERIALIZER_ERROR_RESPONSE(serializer)
        return responses.DEFAULT_400_RESPONSE()

    @action(detail=False, methods=['get','post','patch','delete'])
    def albums(self, request, *args, **kwargs):
        """
        """
        artist = request.user.artist
        album_queryset = self.platform.HiddenAlbums.filter(uploaded_by=artist)
        kwargs['context'] = self.get_serializer_context()
        if request.method in ['PATCH','DELETE']:
            album_id = request.data.pop('album_id')

        if request.method == 'GET':
            albums = album_queryset
            serializer = content_ser_v1.AlbumSerializer(albums, many=True)
            return Response(serializer.data)
        
        elif request.method == 'POST':
            if 'platform' not in request.data.keys():
                request.data['platform'] = str(self.platform)
            serializer = content_ser_v1.AlbumSerializer(data=request.data, *args, **kwargs)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            else:
                return responses.SERIALIZER_ERROR_RESPONSE(serializer)
            return responses.DEFAULT_400_RESPONSE()

        elif request.method == 'PATCH':
            instance = album_queryset.get(pk=album_id)

            # ensure editing artist is the uploading artist
            if artist != instance.uploaded_by:
                return Response({"detail": "You are not authorized to edit this album"}, status=status.HTTP_403_FORBIDDEN)

            serializer = content_ser_v1.AlbumSerializer(data=request.data, instance=instance, partial=True, *args, **kwargs)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            else:
                return responses.SERIALIZER_ERROR_RESPONSE(serializer)
            return responses.DEFAULT_400_RESPONSE()

        elif request.method == 'DELETE':
            instance = album_queryset.get(pk=album_id)

            # ensure editing artist is the uploading artist
            if artist != instance.uploaded_by:
                return Response({"detail": "You are not authorized to delete this album"}, status=status.HTTP_403_FORBIDDEN)

            instance.is_deleted = True
            instance.is_displayed = False
            instance.save()
            return responses.DELETED()

        else:
            return responses.NO_REQUEST_TYPE()

    @action(detail=False, methods=['get','post','patch','delete'])
    def songs(self, request, *args, **kwargs):
        artist = request.user.artist
        song_queryset = self.platform.HiddenSongs.filter(uploaded_by=artist)
        album_queryset = self.platform.HiddenAlbums.filter(uploaded_by=artist)
        kwargs['context'] = self.get_serializer_context()
        if request.method in ['PATCH','DELETE']:
            song_id = request.data.pop('song_id')

        if request.method == 'GET':
            songs = song_queryset

            params = request.query_params
            if 'album_id' in params.keys():
                songs = songs.filter(album=album_queryset.get(pk=params['album_id']))

            serializer = content_ser_v1.SongSerializer(songs, many=True)
            return Response(serializer.data)

        elif request.method == 'POST':
            if 'platform' not in request.data.keys():
                request.data['platform'] = str(self.platform)
            serializer = content_ser_v1.SongSerializer(data=request.data, *args, **kwargs)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            else:
                return responses.SERIALIZER_ERROR_RESPONSE(serializer)
            return responses.DEFAULT_400_RESPONSE()

        elif request.method == 'PATCH':
            instance = song_queryset.get(pk=song_id)

            # ensure this artist uploaded this song
            if artist != instance.uploaded_by:
                return Response({"detail": "You are not authorized to edit this song"}, status=status.HTTP_403_FORBIDDEN)

            serializer = content_ser_v1.SongSerializer(data=request.data, instance=instance, partial=True, *args, **kwargs)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            else:
                return responses.SERIALIZER_ERROR_RESPONSE(serializer)
            return responses.DEFAULT_400_RESPONSE()

        elif request.method == 'DELETE':
            instance = song_queryset.get(pk=song_id)

            # ensure this artist uploaded this song
            if artist != instance.uploaded_by:
                return Response({"detail": "You are not authorized to edit this song"}, status=status.HTTP_403_FORBIDDEN)

            instance.is_deleted = True
            instance.is_displayed = False
            instance.save()
            return responses.DELETED()
        
        else:
            return responses.NO_REQUEST_TYPE()

    @action(detail=False)
    def contributions(self, request):
        artist = request.user.artist
        songs = self.platform.HiddenSongContributors.filter(artist=artist, primary_artist=False)
        albums = self.platform.HiddenAlbumContributions.filter(artist=artist, primary_artist=False, album__is_displayed=True)
        song_serializer = content_ser_v1.SongContributorSerializer(songs, many=True)
        album_serializer = content_ser_v1.AlbumContributorSerializer(albums, many=True)
        return Response({
            'songs': song_serializer.data,
            'albums': album_serializer.data
        })
    
    @action(detail=False, methods=['get','post','patch','delete'], url_path='contributions/albums')
    def album_contributions(self, request, *args, **kwargs):
        artist = request.user.artist
        albumcontribution_queryset = self.platform.HiddenAlbumContributions.filter(artist=artist, primary_artist=False)
        kwargs['context'] = self.get_serializer_context()
        if request.method in ['PATCH','DELETE']:
            contribution_id = request.data['contribution_id']

        if request.method == 'GET':
            albums = albumcontribution_queryset
            album_serializer = content_ser_v1.AlbumContributorSerializer(albums, many=True)
            return Response(album_serializer.data)
        
        if request.method == 'POST':
            serializer = content_ser_v1.AlbumContributorSerializer(data=request.data, *args, **kwargs)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            else:
                return responses.SERIALIZER_ERROR_RESPONSE(serializer)
            return responses.DEFAULT_400_RESPONSE()

        elif request.method == 'PATCH':
            instance = albumcontribution_queryset.get(pk=contribution_id)

            # check that the current artist is the album's uploading artist
            if artist != instance.album.uploaded_by:
                return Response({"detail": "You are not authorized to edit this contribution"}, status=status.HTTP_403_FORBIDDEN)

            serializer = BaseAlbumContributorSerializer(data=request.data, instance=instance, partial=True, *args, **kwargs)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            else:
                return responses.SERIALIZER_ERROR_RESPONSE(serializer)
            return responses.DEFAULT_400_RESPONSE()

        elif request.method == 'DELETE':
            instance = albumcontribution_queryset.get(pk=contribution_id)

            # check that the current artist is the album's uploading artist
            if (artist != instance.album.uploaded_by) or (artist != instnace.artist):
                return Response({"detail": "You are not authorized to delete this contribution"}, status=status.HTTP_403_FORBIDDEN)

            instance.delete()
            return resposnes.DELETED()

        else:
            return responses.NO_REQUEST_TYPE()
    
    @action(detail=False, url_path='contributions/songs', methods=['get','post','patch','delete'])
    def song_contributions(self, request, *args, **kwargs):
        artist = request.user.artist
        songcontribution_queryset = self.platform.HiddenSongContributors.filter(artist=artist, primary_artist=False)
        full_queryset = SongContributor.objects.all()
        kwargs['context'] = self.get_serializer_context()
        if request.method in ['PATCH','DELETE']:
            contribution_id = request.data.pop('contribution_id')

        if request.method == 'GET':
            songs = songcontribution_queryset
            song_serializer = content_ser_v1.SongContributorSerializer(songs, many=True, *args, **kwargs)

            return Response(song_serializer.data)

        elif request.method == 'POST':
            serializer = content_ser_v1.SongContributorSerializer(data=request.data, *args, **kwargs)
            if serializer.is_valid():
                serializer.save()
                return responses.CREATED(serializer)
            else:
                return responses.SERIALIZER_ERROR_RESPONSE(serializer)
            return responses.DEFAULT_400_RESPONSE()

        elif request.method == 'PATCH':
            instance = full_queryset.get(pk=contribution_id)

            if artist != instance.song.uploaded_by:
                return Response({"detail": "You are not authorized to edit this contribution"}, status=status.HTTP_403_FORBIDDEN)

            serializer = content_ser_v1.SongContributorSerializer(instance=instance, data=data, partial=True, *args, **kwargs)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            else:
                return responses.SERIALIZER_ERROR_RESPONSE(serializer)
            return responses.DEFAULT_400_RESPONSE()

        elif request.method == 'DELETE':
            instance = full_queryset.get(pk=contribution_id)

            if (artist != instance.song.uploaded_by) or (artist != instance.artist):
                return Response({"detail": "You are not authorized to delete this contribution"}, status=status.HTTP_403_FORBIDDEN)

            instance.delete()
            return responses.DELETED()
        
        else:
            return responses.NO_REQUEST_TYPE()

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
