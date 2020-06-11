"""
Created: 10 June 2020
"""

import datetime

from revibe.exceptions import api

from administration.models import ArtistOfTheWeek

# -----------------------------------------------------------------------------


def get_current_artist_of_the_week(return_artist: bool=True, date: datetime.date=None):
    """
    """
    starter = datetime.date.today() if not date else date
    time_period = starter - datetime.timedelta(days=6)
    exclude_date = starter + datetime.timedelta(days=1)

    aotws = ArtistOfTheWeek.active_objects.filter(start_date__gte=time_period, start_date__lte=exclude_date).order_by('-start_date')

    if not aotws.exists():
        return None

    aotw = aotws.first()
    if return_artist:
        return aotw.artist
    else:
        return aotw

