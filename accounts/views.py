from django.conf import settings
from rest_framework import viewsets, permissions, generics, status
from rest_framework.response import Response
from rest_auth.registration.views import SocialConnectView
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
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

class UserViewSet(generics.GenericAPIView):
    permission_classes = [permissions.IsAuthenticated, ]
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
               'client_id': CLIENT_ID,
               'client_secret': CLIENT_SECRET,
               # 'scope': []
               }
        req = requests.post('http://127.0.0.1:8000/o/token/',headers=headers,data=data)
        return Response({
            "user": UserSerializer(user, context=self.get_serializer_context()).data,
            "token": req.json()
        })


class LoginAPI(generics.GenericAPIView):
    permission_classes = (permissions.AllowAny,)
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
        return Response({
            "user": UserSerializer(user, context=self.get_serializer_context()).data,
            "token": req.json()
        })

class RefreshTokenAPI(generics.GenericAPIView):
    permission_classes = (permissions.IsAuthenticated,)
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
        return Response(req.json())


@api_view(['POST'])
@permission_classes([AllowAny])
def revoke_token(request):
    '''
    Method to revoke tokens.
    {"token": "<token>"}
    '''
    r = requests.post(
        'http://127.0.0.1:8000/o/revoke_token/',
        data={
            'token': request.data['token'],
            'client_id': CLIENT_ID,
            'client_secret': CLIENT_SECRET,
        },
    )
    # If it goes well return sucess message (would be empty otherwise)
    if r.status_code == requests.codes.ok:
        return Response({'message': 'token revoked'}, r.status_code)
    # Return the error if it goes badly
    return Response(r.json(), r.status_code)

class UserArtistViewSet(ProtectedResourceView):
    # permission_classes = [permissions.IsAuthenticated]
    serializer_class = UserArtistSerializer
    http_method_names = ['post']

    def get_queryset(self):
        return self.request.user.artist

    def create(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            artist = serializer.save()
            request.user.artist = artist
            request.user.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

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
    # permission_classes = (permissions.IsAuthenticated,)
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




# TODO: rewrite as class with serializer
# @api_view(['POST'])
# def refresh_spotify_token(request):
#     token_str = request.GET.get('authToken')
#     access_token = Token.objects.get(key=token_str)
#     user = access_token.user
#     if not user:
#         return Response({"error":"No user found."},status=status.HTTP_400_BAD_REQUEST)
#
#     if SocialAccount.objects.filter(user=user,provider="spotify").exists():
#         social_account = SocialAccount.objects.get(user=user,provider="spotify")
#
#         if SocialToken.objects.filter(account=social_account).exists():
#             token = SocialToken.objects.get(account=social_account)
#             spotify = SocialApp.objects.get(name="Spotify")
#             clientid = spotify.client_id
#             secretkey= spotify.secret
#             refreshkey = token.token_secret
#             try:
#                 spotifyurl = "https://accounts.spotify.com/api/token"
#                 spotifydata = {'grant_type': 'refresh_token', 'refresh_token':refreshkey}
#                 response = requests.post(spotifyurl, data=spotifydata, auth=(clientid, secretkey))
#                 response = json.loads(response.text)
#                 token.token = response['access_token']
#                 token.save()
#                 return Response({'access_token':response['access_token'],'refresh_token':refreshkey, "expires_in": 3600}, status=status.HTTP_200_OK)
#             except:
#                 return Response({'access_token': token.token,'refresh_token':token.token_secret}, status=status.HTTP_200_OK)
#         else:
#             return Response({"error":"Social Token does not exist."},status=status.HTTP_400_BAD_REQUEST) # should probably return current tokens
#
#     # need to handle errors here
#     else:
#         return Response({"error":"Social Account for provider='Spotify' and user="+user.email+" does not exist."},status=status.HTTP_400_BAD_REQUEST) # should probably return current tokens


# # rewrite as class with serializer
# @api_view(['GET'])
# def get_connected_platforms(request):
#     user = request.user
#     print(user)
#     social_tokens = []
#     if SocialAccount.objects.filter(user=user).exclude(provider="Google").exists():
#         for social_account in SocialAccount.objects.filter(user=user).exclude(provider="Google"):
#             social_account_obj = SocialAccount.objects.get(user=user, provider=social_account.provider)
#             if SocialToken.objects.filter(account=social_account_obj).exists():
#                 social_token = SocialToken.objects.get(account=social_account_obj)
#                 social_tokens.append({"name":social_account.provider.title(), "access_token":social_token.token, "refresh_token":social_token.token_secret})
#
#     return Response({"platforms": social_tokens},status=status.HTTP_200_OK)
