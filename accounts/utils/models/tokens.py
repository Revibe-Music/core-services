"""
Created: 28 Apr. 2020
Author: Jordan Prechac
"""

from oauth2_provider.models import AccessToken

# -----------------------------------------------------------------------------

def delete_old_tokens(user):
    """
    """
    tokens = AccessToken.objects.filter(user=user)
    for at in tokens:
        at.source_refresh_token.delete()
        at.delete()
