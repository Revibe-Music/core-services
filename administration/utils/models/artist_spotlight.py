"""
Created 2 Mar. 2020
Author: Jordan Prechac
"""

import datetime

from revibe._errors.network import BadRequestError

from administration.models import ArtistSpotlight
from content.models import Artist

from . artist_of_the_week import get_current_artist_of_the_week

# -----------------------------------------------------------------------------


def todays_artist_spotlight():
    """
    If there is an artist spotlight for today, return that artist object
    """
    today = datetime.date.today()

    # get today's artist spotlight, if there is one
    try:
        spotlight = ArtistSpotlight.objects.get(date=today)
    except ArtistSpotlight.DoesNotExist as e:
        pass
    else:
        if spotlight.artist.artist_profile.hide_all_content == True:
            return None
        return spotlight.artist

    # if there isn't a spotlight for today, get this week's Artist of the Week
    artist = get_current_artist_of_the_week(return_artist=True)
    if artist.artist_profile.hide_all_content:
        return None
    return artist


