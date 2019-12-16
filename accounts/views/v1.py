from django.conf import settings
from django.db.models import Q
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

from artist_portal._errors.random import ValidationError
from accounts.permissions import TokenOrSessionAuthentication
from accounts.models import *
from accounts.serializers.v1 import *
from music.models import Album, Song, SongContributor, AlbumContributor
from music.serializers import v1 as ser_v1
from music.queries import *

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

class UserArtistViewSet(viewsets.GenericViewSet):
    """
    Endpoint: account/artist/
        Get: 
            Gets the profile information of the authenticated user, assuming they have an artist linked to their account
        Post:
            Creates an artist and attaches it to the current user
            Required data:
                name: (string) artist's display name
                image_up: (file) artist's display image
        Patch:
            Updates the artist's profile information
            Optional data:
                name: (string) artist's display name
                image_up: (file) artist's dispaly image
    
    Endpoint: account/artist/album/
        See the .albums method

    Endpoint: account/artist/song/
        See the .songs method

    Endpoint: /account/artist/contributions/
        See the .contributions method

    Endpoint: /account/artist/contributions/albums/
        See the .album_contributions method

    Endpoint: account/artist/contributions/songs/
        See the .song_contributions method
    """
    queryset = CustomUser.objects.all()
    permission_classes = [TokenOrSessionAuthentication]
    required_alternate_scopes = {
        'GET': [['ADMIN'],['first-party']],
        'POST': [['ADMIN'],['first-party']],
        'PATCH': [['ADMIN'],['first-party']],
        'PUT': [['ADMIN'],['first-party']],
        'DELETE': [['ADMIN'],['first-party']],
    }
    serializer_class = UserArtistSerializer

    def list(self, request):
        if not request.user.artist:
            return Response({"detail": "could not identify the current user's artist profile"}, status=status.HTTP_401_UNAUTHORIZED)

        artist = self.serializer_class(request.user.artist, context=self.get_serializer_context()).data
        return Response(artist)

    def create(self, request):
        # check if user already has an artist object
        if request.user.artist != None:
            return Response({"detail": "this user already has an artist account"}, status=status.HTTP_400_BAD_REQUEST)        
        
        # create the artist and attach to the user
        request.data['platform'] = 'Revibe'
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            artist = serializer.save()
            request.user.artist = artist
            request.user.is_artist = True
            request.user.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request, *args, **kwargs):
        instance = request.user.artist
        serializer = self.get_serializer(data=request.data, instance=instance, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data)
    
    @action(detail=False, methods=['get','post','patch','delete'])
    def albums(self, request, *args, **kwargs):
        """
        URL endpoint for all artist album-related requests.
        Takes GET, POST, PATCH, and DELETE requests.

        Endpoint: /account/artist/albums/
            GET:
            POST:
            PATCH:
            DELETE:
            TODO: write docs
        """
        artist = request.user.artist
        album_queryset = RevibeHiddenAlbums.filter(uploaded_by=artist)
        kwargs['context'] = self.get_serializer_context()
        if request.method in ['PATCH','DELETE']:
            album_id = request.data.pop('album_id')

        if request.method == 'GET':
            albums = album_queryset
            serializer = ser_v1.BaseAlbumSerializer(albums, many=True)
            return Response(serializer.data)
        
        elif request.method == 'POST':
            if 'platform' not in request.data.keys():
                request.data['platform'] = 'Revibe'
            serializer = ser_v1.BaseAlbumSerializer(data=request.data, *args, **kwargs)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        
        elif request.method == 'PATCH':
            instance = album_queryset.get(pk=album_id)

            # ensure editing artist is the uploading artist
            if artist != instance.uploaded_by:
                return Response({"detail": "You are not authorized to edit this album"}, status=status.HTTP_403_FORBIDDEN)

            serializer = ser_v1.BaseAlbumSerializer(data=request.data, instance=instance, partial=True, *args, **kwargs)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        
        elif request.method == 'DELETE':
            instance = RevibeHiddenAlbums.get(pk=album_id)

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
        """
        The URL endpoint for all artist song-related requests
        Takes GET, POST, PATCH, and DELETE requests

        Endpoint: /account/artist/songs/
            GET:
            POST:
            PATCH:
            DELETE:
            TODO: write docs
        """
        artist = request.user.artist
        song_queryset = RevibeHiddenSongs.filter(uploaded_by=artist)
        kwargs['context'] = self.get_serializer_context()
        if request.method in ['PATCH','DELETE']:
            song_id = request.data.pop('song_id')

        if request.method == 'GET':
            songs = song_queryset
            serializer = ser_v1.BaseSongSerializer(songs, many=True)
            return Response(serializer.data)

        elif request.method == 'POST':
            serializer = ser_v1.BaseSongSerializer(data=request.data, *args, **kwargs)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        elif request.method == 'PATCH':
            instance = song_queryset.get(pk=song_id)

            # ensure this artist uploaded this song
            if artist != instance.uploaded_by:
                return Response({"detail": "You are not authorized to edit this song"}, status=status.HTTP_403_FORBIDDEN)

            serializer = ser_v1.BaseSongSerializer(data=request.data, instance=instance, partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)

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
        songs = SongContributor.objects.filter(artist=artist)
        albums = AlbumContributor.objects.filter(artist=artist)
        song_serializer = SongSongContributorSerializer(songs, many=True)
        album_serializer = AlbumAlbumContributorSerializer(albums, many=True)
        return Response({
            'songs': song_serializer.data,
            'albums': album_serializer.data
        })
    
    @action(detail=False, methods=['get','post','patch','delete'], url_path='contributions/albums')
    def album_contributions(self, request, *args, **kwargs):
        """
        """
        artist = request.user.artist
        kwargs['context'] = self.get_serializer_context()
        if request.method in ['patch','delete']:
            contribution_id = request.data['contribution_id']

        if request.method == 'GET':
            albums = AlbumContributor.objects.filter(artist=artist, primary_artist=False, album__is_displayed=True)
            album_serializer = ser_v1.AlbumAlbumContributorSerializer(albums, many=True)
            return Response(album_serializer.data)
        
        if request.method == 'POST':
            serializer = ser_v1.BaseAlbumContributorSerializer(data=request.data, *args, **kwargs)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        elif request.method == 'PATCH':
            instance = AlbumContributor.objects.get(pk=contribution_id)

            # check that the current artist is the album's uploading artist
            if artist != instance.song.uploaded_by:
                return Response({"detail": "You are not authorized to edit this contribution"}, status=status.HTTP_403_FORBIDDEN)

            serializer = BaseAlbumContributorSerializer(data=request.data, instance=instance, partial=True, *args, **kwargs)
            serializer.is_valid(raise_exception=True)
            serializer.save()

            return Response(serializer.data, status=status.HTTP_201_CREATED)

        elif request.method == 'DELETE':
            instance = AlbumContributor.objects.get(pk=contribution_id)

            # check that the current artist is the album's uploading artist
            if artist != instance.song.uploaded_by:
                return Response({"detail": "You are not authorized to edit this contribution"}, status=status.HTTP_403_FORBIDDEN)

            instance.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

        else:
            return Response({"detail": "could no identify request type"}, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, url_path='contributions/songs', methods=['get','post','patch','delete'])
    def song_contributions(self, request, *args, **kwargs):
        """
        URL Endpoint for handling all of the authenticated artist's song contributor information.
        Takes GET, POST, PATCH, and DELETE requests.

        Endpoint: /v1/account/artist/contributions/songs/
            Get:
                nothing special
            Post:
                Required data:
                    song: the song's ID
                    artist: the contributing artist's ID
                    contribution_type: string
            Patch:
                Can only update the contribution type - cannot change the artist or the song.
                We will just force users to create new contributions for that purpose. 

                Required data:
                    contribution_id: the contribution ID
                    contribution_type: string
            Delete:
                Required data:
                    contribution_id: the contribution ID
        """
        artist = request.user.artist
        kwargs['context'] = self.get_serializer_context()
        if request.method in ['PATCH','DELETE']:
            contribution_id = request.data.pop('contribution_id')

        if request.method == 'GET':
            songs = SongContributor.objects.filter(artist=artist, primary_artist=False, song__is_displayed=True)
            song_serializer = ser_v1.SongSongContributorSerializer(songs, many=True, *args, **kwargs)

            return Response(song_serializer.data)

        elif request.method == 'POST':
            serializer = ser_v1.BaseSongContributorSerialzer(data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        elif request.method == 'PATCH':
            partial = kwargs.pop('partial', False)
            instance = SongContributor.objects.get(pk=contribution_id)

            serializer = ser_v1.BaseSongContributorSerialzer(instance=instance, data=data, partial=partial, *args, **kwargs)
            serializer.is_valid(raise_exception=True)
            serializer.save()

            return Response(serializer.data, status=status.HTTP_201_CREATED)

        elif request.method == 'DELETE':
            instance = SongContributor.objects.get(pk=contribution_id)
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
