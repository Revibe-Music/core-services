from django.conf import settings
from rest_framework import viewsets, permissions, generics, status
from rest_framework.response import Response
from knox.models import AuthToken
from rest_auth.registration.views import SocialConnectView
from allauth.socialaccount.providers.spotify.views import SpotifyOAuth2Adapter
from allauth.socialaccount.providers.oauth2.client import OAuth2Client
from allauth.socialaccount.models import SocialAccount, SocialToken, SocialApp
from .models import *
from .serializers import *
import requests
import json


class UserViewSet(generics.GenericAPIView):
    permission_classes = [permissions.IsAuthenticated, ]
    serializer_class = UserSerializer

    def get(self, request):
        return Response(
            UserSerializer(request.user, context=self.get_serializer_context()).data
        )
    
    # TODO: define the update-user stuff here
    def patch(self, request):
        return None

class RegistrationAPI(generics.GenericAPIView):
    serializer_class = UserSerializer
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return Response({
            "user": UserSerializer(user, context=self.get_serializer_context()).data,
            "token": AuthToken.objects.create(user)[1]
        })

class LoginAPI(generics.GenericAPIView):
    permission_classes = (permissions.AllowAny,)
    serializer_class = LoginAccountSerializer
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data
        return Response({
            "user": AccountSerializer(user, context=self.get_serializer_context()).data,
            "token": AuthToken.objects.create(user)[1]
        })

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


class UserArtistViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated]
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
