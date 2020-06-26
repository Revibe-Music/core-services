"""
"""

from allauth.socialaccount.providers.google.views import GoogleOAuth2Adapter

from .provider import GoogleProviderWeb, GoogleProviderMobile


class GoogleOAuth2AdapterWeb(GoogleOAuth2Adapter):
    provider_id = GoogleProviderWeb.id

class GoogleOAuth2AdapterMobile(GoogleOAuth2Adapter):
    provider_id = GoogleProviderMobile.id