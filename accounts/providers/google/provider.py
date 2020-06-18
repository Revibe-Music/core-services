"""
"""

from allauth.socialaccount.providers.google.provider import GoogleProvider

# -----------------------------------------------------------------------------


class GoogleProviderWeb(GoogleProvider):
    id = 'google-web'
    name = 'Google Web'

class GoogleProviderMobile(GoogleProvider):
    id = 'google-mobile'
    name = 'Google Mobile'



