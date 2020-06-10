"""
Created: 10 June 2020
"""

import datetime

from revibe.exceptions import api

from administration.models import ArtistOfTheWeek

# -----------------------------------------------------------------------------


def get_current_artist_of_the_week(return_artist: bool=True):
    """
    """
    today = datetime.date.today()
    time_period = today - datetime.timedelta(days=6)

    aotws = ArtistOfTheWeek.objects.filter(start_date__gte=time_period).order_by('-start_date')

    if not aotws.exists():
        return None

    aotw = aotws.first()
    if return_artist:
        return aotw.artist
    else:
        return aotw

