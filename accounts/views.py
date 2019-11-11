from django.conf import settings
from rest_framework import viewsets, permissions, generics, status
from rest_framework.response import Response
from rest_auth.registration.views import SocialConnectView
from allauth.socialaccount.providers.spotify.views import SpotifyOAuth2Adapter
from allauth.socialaccount.providers.oauth2.client import OAuth2Client
from allauth.socialaccount.models import SocialAccount, SocialToken, SocialApp
from oauth2_provider.views.generic import ProtectedResourceView
from oauth2_provider.contrib.rest_framework import TokenHasReadWriteScope
from .models import *
from .serializers import *
import requests
import json

CLIENT_ID = 'y2iPQuosC9qgIJZua9w5VCpHMTdO7Onkl2RF9qQk'
CLIENT_SECRET = 'KE5IMAxQizJAwRKkKUY244PctidKPL88mQwyGPX6ci9ZymHsYSgxxTLeJNMppf1lerlNfjQnKYpZ1xzlsRFtdV6S9gLfb6WdFnVu29BSw8lteoqiU6ZoJtnxabs4slgs'


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
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        headers={"Content-Type": "application/x-www-form-urlencoded"}
        data= {
               'grant_type': 'password',
               'username': request.data['username'],
               'password': request.data['password'],
               'client_id': "y2iPQuosC9qgIJZua9w5VCpHMTdO7Onkl2RF9qQk",
               'client_secret': "KE5IMAxQizJAwRKkKUY244PctidKPL88mQwyGPX6ci9ZymHsYSgxxTLeJNMppf1lerlNfjQnKYpZ1xzlsRFtdV6S9gLfb6WdFnVu29BSw8lteoqiU6ZoJtnxabs4slgs",
               }
        req = requests.post('http://127.0.0.1:8000/o/token/',headers=headers,data=data)
        if req.status_code != 200:
            return Response(req.json(), status=status.HTTP_400_BAD_REQUEST)

        return Response({
            "user": UserSerializer(user, context=self.get_serializer_context()).data,
            "token": req.json()
        })

class LoginAPI(generics.GenericAPIView):
    permission_classes = [permissions.AllowAny]
    serializer_class = LoginAccountSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data
        headers={"Content-Type": "application/x-www-form-urlencoded"}
        data= {
               'grant_type': 'password',
               'username': request.data['username'],
               'password': request.data['password'],
               'client_id': CLIENT_ID,
               'client_secret': CLIENT_SECRET
               }
        req = requests.post('http://127.0.0.1:8000/o/token/',headers=headers,data=data)
        if req.status_code != 200:
            return Response(req.json(), status=status.HTTP_400_BAD_REQUEST)
        return Response({
            "user": UserSerializer(user, context=self.get_serializer_context()).data,
            "token": req.json()
        })

class RefreshTokenAPI(generics.GenericAPIView):
    permission_classes = [permissions.AllowAny]
    serializer_class = RefreshTokenSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data
        headers={"Content-Type": "application/x-www-form-urlencoded"}
        data= {
               'grant_type': 'refresh_token',
               'refresh_token': request.data['refresh_token'],
               'client_id': CLIENT_ID,
               'client_secret': CLIENT_SECRET
               }
        req = requests.post('http://127.0.0.1:8000/o/token/',headers=headers,data=data)
        if req.status_code != 200:
            return Response(req.json(), status=status.HTTP_400_BAD_REQUEST)
        return Response(req.json())

class LogoutAPI(generics.GenericAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = AccessTokenSerializer

    def post(self, request, *args, **kwargs):
        headers={"Content-Type": "application/x-www-form-urlencoded"}
        data= {
               'token': request.data['access_token'],
               'client_id': CLIENT_ID,
               'client_secret': CLIENT_SECRET
               }
        req = requests.post('http://127.0.0.1:8000/o/revoke_token/',headers=headers,data=data)
        if req.status_code != 200:
            return Response(req.json(), status=status.HTTP_400_BAD_REQUEST)
        return Response({"status":"success", "code":200, "message": "Token has been revoked."})

class SpotifyConnect(SocialConnectView):
    """ Logs already authenticated user into Spotify account"""
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


class SpotifyRefresh(ProtectedResourceView):
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = UserSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data
        if SocialAccount.objects.filter(user=user,provider="spotify").exists():
            social_account = SocialAccount.objects.get(user=user,provider="spotify")
            if SocialToken.objects.filter(account=social_account).exists():
                token = SocialToken.objects.get(account=social_account)
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
    serializer_class = UserSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data
        if SocialAccount.objects.filter(user=user,provider="spotify").exists():
            social_account = SocialAccount.objects.get(user=user,provider="spotify")
            social_account.delete()
            return Response({'message':'Spotify logout successful.'}, status=status.HTTP_200_OK)
        return Response({"error":"User has not logged into Spotify."},status=status.HTTP_400_BAD_REQUEST) # should probably return current tokens

class UserArtistViewSet(generics.GenericAPIView):
    permission_classes = [permissions.IsAuthenticated, TokenHasReadWriteScope]
    serializer_class = UserArtistSerializer

    def get(self):
        return self.request.user.artist

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            artist = serializer.save()
            request.user.artist = artist
            request.user.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class UserViewSet(generics.GenericAPIView):
    permission_classes = [permissions.IsAuthenticated, TokenHasReadWriteScope]
    serializer_class = UserSerializer

    def get(self, request, *args, **kwargs):
        return Response(UserSerializer(request.user, context=self.get_serializer_context()).data)

    def patch(self, request, *args, **kwargs):
        user = request.user
        if request.data['first_name']:
            user.first_name = request.data['first_name']
        if request.data['last_name']:
            user.last_name = request.data['last_name']
        if request.data['username']:
            user.username = request.data['username']
        if request.data['email']:
            user.email = request.data['email']
        if request.data['profile']['country']:
            user.profile.country = request.data['profile']['country']
        if request.data['profile']['image']:
            user.profile.image = request.data['profile']['image']
        user.save()
        user.profile.save()

class UserConnectedPlatforms(generics.GenericAPIView):
    permission_classes = [permissions.IsAuthenticated, TokenHasReadWriteScope]
    serializer_class = SocialTokenSerializer

    def get(self, request, *args, **kwargs):
        return Response(SocialTokenSerializer(request.user, context=self.get_serializer_context()).data)
