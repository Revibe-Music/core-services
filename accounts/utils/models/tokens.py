"""
Created: 28 Apr. 2020
Author: Jordan Prechac
"""

from django.utils import timezone
from oauth2_provider.models import AccessToken, Application, RefreshToken
from oauthlib import common

import datetime

from revibe._helpers import const

# -----------------------------------------------------------------------------

def delete_old_tokens(user):
    """
    """
    tokens = AccessToken.objects.filter(user=user)
    for at in tokens:
        at.source_refresh_token.delete()
        at.delete()


def create_access_token(user, device="phone", return_refresh=True, *args, **kwargs):
    app = Application.objects.get(name="Revibe First Party Application")

    scopes = ['first-party']
    if device == 'browser':
        scopes.append('artist')
    scope = " ".join(scopes)

    time = const.BROWSER_EXPIRY_TIME if device == 'browser' else const.DEFAULT_EXPIRY_TIME
    expire = timezone.now() + datetime.timedelta(hours=time)

    access_token = AccessToken.objects.create(
        user=user,
        expires=expire,
        token=common.generate_token(),
        application=app,
        scope=scope
    )
    refresh_token = RefreshToken.objects.create(
        user=user,
        token=common.generate_token(),
        application=app,
        access_token=access_token
    )
    access_token.source_refresh_token = refresh_token
    access_token.save()

    if return_refresh:
        return access_token, refresh_token
    else:
        return access_token
