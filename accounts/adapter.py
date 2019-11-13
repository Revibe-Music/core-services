from allauth.account.adapter import DefaultAccountAdapter
from django.forms import ValidationError
from rest_framework.authentication import TokenAuthentication
from oauth2_provider.contrib.rest_framework import OAuth2Authentication
from oauth2_provider.backends import OAuth2Backend, get_oauthlib_core
from oauth2_provider.models import AccessToken
# from oauth2_provider.settings import ACCESS_TOKEN_MODEL


class TokenAuthSupportQueryString(OAuth2Authentication):
    """
    Extend the TokenAuthentication class to support querystring authentication
    in the form of "http://www.example.com/?authToken=<token_key>"
    """
    def authenticate(self, request):

        # Check if 'authToken' is in the request query params.
        # Give precedence to 'Authorization' header.
        # if 'authToken' in request.query_params and 'HTTP_AUTHORIZATION' not in request.META:
        if 'authToken' in request.query_params:
            if(AccessToken.objects.filter(token=request.query_params.get('authToken')).exists()):
                access_token = AccessToken.objects.get(token=request.query_params.get('authToken'))
                return access_token.user, access_token
        else:
            return super(TokenAuthSupportQueryString, self).authenticate(request)


# class TokenAuthSupportQueryString(TokenAuthentication):
#     """
#     Extend the TokenAuthentication class to support querystring authentication
#     in the form of "http://www.example.com/?authToken=<token_key>"
#     """
#     def authenticate(self, request):
#         # Check if 'token_auth' is in the request query params.
#         # Give precedence to 'Authorization' header.
#         if 'authToken' in request.query_params and 'HTTP_AUTHORIZATION' not in request.META:
#             return self.authenticate_credentials(request.query_params.get('authToken'))
#         else:
#             return super(TokenAuthSupportQueryString, self).authenticate(request)
