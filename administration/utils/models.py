"""
Created 2 Mar. 2020
Author: Jordan Prechac
"""

import datetime

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
    
    return spotlight.artist
