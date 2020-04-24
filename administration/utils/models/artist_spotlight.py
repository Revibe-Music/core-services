"""
Created 2 Mar. 2020
Author: Jordan Prechac
"""

import datetime

from revibe._errors.network import BadRequestError

from administration.models import ArtistSpotlight
from content.models import Artist

# -----------------------------------------------------------------------------


def todays_artist_spotlight():
    """
    If there is an artist spotlight for today, return that artist object
    """
    today = datetime.date.today()

    try:
        spotlight = ArtistSpotlight.objects.get(date=today)
    except ArtistSpotlight.DoesNotExist as e:
        return None
    
    if spotlight.artist.artist_profile.hide_all_content == True:
        return None
    
    return spotlight.artist


