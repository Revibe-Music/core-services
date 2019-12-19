from django.conf import settings
from rest_framework import viewsets, permissions, generics, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_auth.registration.views import SocialConnectView
from allauth.socialaccount.providers.spotify.views import SpotifyOAuth2Adapter
from allauth.socialaccount.providers.oauth2.client import OAuth2Client
from allauth.socialaccount.models import SocialAccount, SocialToken, SocialApp
from oauth2_provider.views import TokenView, RevokeTokenView
from oauth2_provider.contrib.rest_framework import TokenHasReadWriteScope,TokenMatchesOASRequirements, TokenHasScope
from oauth2_provider.models import Application
import requests
import json
from django.http import HttpRequest

from artist_portal.viewsets import GenericPlatformViewSet
from artist_portal._errors.random import ValidationError
from accounts.permissions import TokenOrSessionAuthentication
from accounts.models import *
from accounts.serializers.v1 import *
from content.models import Album, Song, SongContributor, AlbumContributor
from content.serializers import v1 as content_ser_v1
from music.serializers import v1 as music_ser_v1

class RegistrationAPI(generics.GenericAPIView, TokenView):
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
        serializer.is_valid(raise_exception=True)
        application = Application.objects.get(name="Revibe First Party Application")
        user = serializer.save()
        headers={"Content-Type": "application/x-www-form-urlencoded"}
        data= {
               'grant_type': 'password',
               'username': request.data['username'],
               'password': request.data['password'],
               'client_id': application.client_id,
               'client_secret': application.client_secret,
               }
        auth_request = HttpRequest()
        auth_request.method = "POST"
        auth_request.POST = data
        auth_request.content_type = "application/x-www-form-urlencoded"
        req = TokenView.post(self, auth_request)
        if req.status_code != 200:
            return Response(req.json(), status=status.HTTP_400_BAD_REQUEST)

        return Response({
            "user": UserSerializer(user, context=self.get_serializer_context()).data,
            "token": json.loads(req.content.decode('utf-8'))
        })

class LoginAPI(generics.GenericAPIView, TokenView):
    permission_classes = [permissions.AllowAny]
    serializer_class = LoginAccountSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        application = Application.objects.get(name="Revibe First Party Application")
        user = serializer.validated_data
        headers={"Content-Type": "application/x-www-form-urlencoded"}
        data= {
               'grant_type': 'password',
               'username': request.data['username'],
               'password': request.data['password'],
               'client_id': application.client_id,
               'client_secret': application.client_secret
               }
        auth_request = HttpRequest()
        auth_request.method = "POST"
        auth_request.POST = data
        auth_request.content_type = "application/x-www-form-urlencoded"
        req = TokenView.post(self, auth_request)
        if req.status_code != 200:
            return Response(req.json(), status=status.HTTP_400_BAD_REQUEST)
        return Response({
            "user": UserSerializer(user, context=self.get_serializer_context()).data,
            "token": json.loads(req.content.decode('utf-8'))
        })

class RefreshTokenAPI(generics.GenericAPIView, TokenView):
    permission_classes = [permissions.AllowAny]
    serializer_class = RefreshTokenSerializer

    def post(self, request, *args, **kwargs):
        application = Application.objects.get(name="Revibe First Party Application")
        headers={"Content-Type": "application/x-www-form-urlencoded"}
        data= {
               'grant_type': 'refresh_token',
               'refresh_token': request.data['refresh_token'],
               'client_id': application.client_id,
               'client_secret': application.client_secret
               }
        auth_request = HttpRequest()
        auth_request.method = "POST"
        auth_request.POST = data
        auth_request.content_type = "application/x-www-form-urlencoded"
        req = TokenView.post(self, auth_request)
        if req.status_code != 200:
            return Response(json.loads(req.content.decode('utf-8')), status=status.HTTP_400_BAD_REQUEST)
        return Response(json.loads(req.content.decode('utf-8')))

class LogoutAPI(generics.GenericAPIView, RevokeTokenView):
    permission_classes = [TokenHasScope]
    required_scopes = []
    serializer_class = AccessTokenSerializer

    def post(self, request, *args, **kwargs):
        application = Application.objects.get(name="Revibe First Party Application")
        headers={"Content-Type": "application/x-www-form-urlencoded"}
        data= {
               'token': request.data['access_token'],
               'client_id': application.client_id,
               'client_secret': application.client_secret
               }
        auth_request = HttpRequest()
        auth_request.method = "POST"
        auth_request.POST = data
        auth_request.content_type = "application/x-www-form-urlencoded"
        req = RevokeTokenView.post(self, auth_request)
        if req.status_code != 200:
            return Response(json.loads(req.content.decode('utf-8')), status=status.HTTP_400_BAD_REQUEST)
        return Response({"status":"success", "code":200, "message": "Token has been revoked."})

class LogoutAllAPI(generics.GenericAPIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, *args, **kwargs):
        application = Application.objects.get(name="Revibe First Party Application")
        AccessToken.objects.filter(user=request.user).delete()
        return Response({"status":"success", "code":200, "message": "All devices have been logged out."})

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
            return Response(serializer.errors, status=status.HTTP_417_EXPECTATION_FAILED)
        return Response({"detail": "Issue processing request, please try again"}, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request, *args, **kwargs):
        instance = request.user.artist
        serializer = self.get_serializer(data=request.data, instance=instance, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        else:
            return Response(serializer.errors, status=status.HTTP_417_EXPECTATION_FAILED)
        return Response({"detail": "Issue processing request, please try again"}, status=status.HTTP_400_BAD_REQUEST)

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
                return Response(serializer.errors, status=status.HTTP_417_EXPECTATION_FAILED)
            return Response({"detail": "Issue processing request, please try again"}, status=status.HTTP_400_BAD_REQUEST)

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
                return Response(serializer.errors, status=status.HTTP_417_EXPECTATION_FAILED)
            return Response({"detail": "Issue processing request, please try again"}, status=status.HTTP_400_BAD_REQUEST)
        
        elif request.method == 'DELETE':
            instance = album_queryset.get(pk=album_id)

            # ensure editing artist is the uploading artist
            if artist != instance.uploaded_by:
                return Response({"detail": "You are not authorized to delete this album"}, status=status.HTTP_403_FORBIDDEN)

            instance.is_deleted = True
            instance.save()
            return Response(status=status.HTTP_204_NO_CONTENT)

        else:
            return Response({"detail": "could no identify request type"}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['get','post','patch','delete'])
    def songs(self, request, *args, **kwargs):
        artist = request.user.artist
        song_queryset = self.platform.HiddenSongs.filter(uploaded_by=artist)
        kwargs['context'] = self.get_serializer_context()
        if request.method in ['PATCH','DELETE']:
            song_id = request.data.pop('song_id')

        if request.method == 'GET':
            songs = song_queryset
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
                return Response(serializer.errors, status=status.HTTP_417_EXPECTATION_FAILED)
            return Response({"detail": "Issue processing request, please try again"}, status=status.HTTP_400_BAD_REQUEST)

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
                return Response(serializer.errors, status=status.HTTP_417_EXPECTATION_FAILED)
            return Response({"detail": "Issue processing request, please try again"}, status=status.HTTP_400_BAD_REQUEST)

        elif request.method == 'DELETE':
            instance = song_queryset.get(pk=song_id)

            # ensure this artist uploaded this song
            if artist != instance.uploaded_by:
                return Response({"detail": "You are not authorized to edit this song"}, status=status.HTTP_403_FORBIDDEN)

            instance.is_deleted = True
            instance.save()
            return Response(status=status.HTTP_204_NO_CONTENT)
        
        else:
            return Response({"detail": "could no identify request type"}, status=status.HTTP_400_BAD_REQUEST)

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
                return Response(serializer.errors, status=status.HTTP_417_EXPECTATION_FAILED)
            return Response({"detail": "Issue processing request, please try again"}, status=status.HTTP_400_BAD_REQUEST)

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
                return Response(serializer.errors, status=status.HTTP_417_EXPECTATION_FAILED)
            return Response({"detail": "Issue processing request, please try again"}, status=status.HTTP_400_BAD_REQUEST)

        elif request.method == 'DELETE':
            instance = albumcontribution_queryset.get(pk=contribution_id)

            # check that the current artist is the album's uploading artist
            if artist != instance.album.uploaded_by:
                return Response({"detail": "You are not authorized to delete this contribution"}, status=status.HTTP_403_FORBIDDEN)

            instance.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

        else:
            return Response({"detail": "could no identify request type"}, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, url_path='contributions/songs', methods=['get','post','patch','delete'])
    def song_contributions(self, request, *args, **kwargs):
        artist = request.user.artist
        songcontribution_queryset = self.platform.HiddenSongContributors.filter(artist=artist, primary_artist=False)
        full_queryset = SongContributor.all_objects.all()
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
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            else:
                return Response(serializer.errors, status=status.HTTP_417_EXPECTATION_FAILED)
            return Response({"detail": "Issue processing request, please try again"}, status=status.HTTP_400_BAD_REQUEST)

        elif request.method == 'PATCH':
            instance = full_queryset.get(pk=contribution_id)

            if artist != instance.song.uploaded_by:
                return Response({"detail": "You are not authorized to edit this contribution"}, status=status.HTTP_403_FORBIDDEN)

            serializer = content_ser_v1.SongContributorSerializer(instance=instance, data=data, partial=True, *args, **kwargs)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            else:
                return Response(serializer.errors, status=status.HTTP_417_EXPECTATION_FAILED)
            return Response({"detail": "Issue processing request, please try again"}, status=status.HTTP_400_BAD_REQUEST)

        elif request.method == 'DELETE':
            instance = full_queryset.get(pk=contribution_id)

            if artist != instance.song.uploaded_by:
                return Response({"detail": "You are not authorized to delete this contribution"}, status=status.HTTP_403_FORBIDDEN)

            instance.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        
        else:
            return Response({"detail": "could no identify request type"}, status=status.HTTP_400_BAD_REQUEST)

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
    
    def get_serializer_class(self):
        serializer_class = self.serializer_class

        if self.request.method == "PATCH":
            serializer_class = UserPatchSerializer
        
        return serializer_class

    def get(self, request, *args, **kwargs):
        return Response(UserSerializer(request.user, context=self.get_serializer_context()).data)

    def patch(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = request.user
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data)
