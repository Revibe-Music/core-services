from django.conf import settings
from rest_framework import viewsets, permissions, generics, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_auth.registration.views import SocialConnectView
from allauth.socialaccount.providers.spotify.views import SpotifyOAuth2Adapter
from allauth.socialaccount.providers.oauth2.client import OAuth2Client
from allauth.socialaccount.models import SocialAccount, SocialToken, SocialApp
from oauth2_provider.views import TokenView, RevokeTokenView
from oauth2_provider.contrib.rest_framework import TokenHasReadWriteScope,TokenMatchesOASRequirements
from oauth2_provider.models import Application
import requests
import json
from django.http import HttpRequest

from .models import *
from .serializers import *
from music.models import Album, Song
from music.serializers import BaseAlbumSerializer, BaseSongSerializer

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
    permission_classes = [permissions.IsAuthenticated]
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
    permission_classes = (permissions.IsAuthenticated,)
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
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        if SocialAccount.objects.filter(user=request.user,provider="spotify").exists():
            social_account = SocialAccount.objects.get(user=request.user,provider="spotify")
            social_account.delete()
            return Response({'message':'Spotify logout successful.'}, status=status.HTTP_200_OK)
        return Response({"error":"User has not logged into Spotify."},status=status.HTTP_400_BAD_REQUEST) # should probably return current tokens


class UserLinkedAccounts(viewsets.ModelViewSet):
    serializer_class = SocialTokenSerializer
    permission_classes = [TokenMatchesOASRequirements]
    required_alternate_scopes = {
        "GET": [["ADMIN"],["read"]]
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
            TODO: implement error send if they do not have a linked artist
        Post:
            Creates an artist and attaches it to the current user
        Patch:
            Used to update user-artist profile information (artist name, image, etc.)
            TODO: implement
    
    Endpoint: account/artist/album/
        Get:
            Gets a list of albums uploaded by the current user.
        Post:
            TODO: implement
            Calls the POST method of the Album viewset.
    
    Endpoint: account/artist/song/
        Get:
            Gets a list of songs uploaded by the current user
        Post:
            TODO: implement
            Calls the POST method of the Song viewset
    """
    queryset = CustomUser.objects.all()
    permission_classes = [permissions.IsAuthenticated, TokenHasReadWriteScope]
    serializer_class = UserArtistSerializer

    def get(self, request):
        artist = self.serializer_class(request.user.artist, context=self.get_serializer_context()).data
        return Response(artist)

    def post(self, request):
        # check if user already has an artist object
        if request.user.artist != None:
            return Response(status=status.HTTP_400_BAD_REQUEST)        
        
        # create the artist and attach to the user
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            artist = serializer.save()
            request.user.artist = artist
            request.user.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request, *args, **kwargs):
        instance = request.user.artist
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data)
    
    @action(detail=False)
    def albums(self, request):
        artist = request.user.artist
        albums = Album.objects.filter(uploaded_by=artist)
        serializer = BaseAlbumSerializer(albums, many=True)
        return Response(serializer.data)
    
    @action(detail=False)
    def songs(self, request):
        artist = request.user.artist
        songs = Song.objects.filter(uploaded_by=artist)
        serializer = BaseSongSerializer(songs, many=True)
        return Response(serializer.data)

class UserViewSet(generics.GenericAPIView):
    permission_classes = [permissions.IsAuthenticated, TokenHasReadWriteScope]
    serializer_class = UserSerializer
    
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
        print(request.data)
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data)
