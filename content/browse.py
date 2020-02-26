"""
Author: Jordan Prechac
Created: 26 Feb. 2020
"""

from django.db.models import Count, Q

import datetime

from content.models import Song, Album
from content.serializers import v1 as cnt_ser_v1
from metrics.models import Stream

# -----------------------------------------------------------------------------

_DEFAULT_LIMIT = 25
today = datetime.datetime.now()
yesterday = today - datetime.timedelta(days=1)
last_week = today - datetime.timedelta(days=7)
last_month = today - datetime.timedelta(days=30)

time_lookup = {
    "today": yesterday, # this naming makes it easier for person making the request. Essentially it's songs popular within the last 24 hours
    "last_week": last_week,
    "last_month": last_month,
}

def _browse_song(annotation, limit=_DEFAULT_LIMIT):
    songs = Song.display_objects.annotate(count=annotation).order_by('-count')[:limit]
    return cnt_ser_v1.SongSerializer(songs, many=True)

def _browse_album(annotation, limit=_DEFAULT_LIMIT):
    albums = Album.display_objects.annotate(count=annotation).order_by('-count')[:limit]
    return cnt_ser_v1.AlbumSerializer(albums, many=True)

# -----------------------------------------------------------------------------
##### all-time #####

# -------------------------------------
# trending songs

def top_songs_all_time(limit=_DEFAULT_LIMIT):
    """
    Retrieve the top played songs on Revibe of all-time
    """
    annotation = Count('streams__id')
    return _browse_song(annotation, limit)


# -------------------------------------
# trending albums

def top_albums_all_time(limit=_DEFAULT_LIMIT):
    """
    Retrieve the top played albums on Revibe of all-time
    """
    annotation = Count('song__streams__id')
    return _browse_album(annotation, limit)


# -----------------------------------------------------------------------------
##### trending #####

# -------------------------------------
# trending songs

def trending_songs(time_period, limit=_DEFAULT_LIMIT):
    assert time_period in time_lookup.keys(), f"Could not find 'time_period' value '{time_period}' in lookup."
    annotation = Count('streams__id', filter=Q(streams__timestamp__gte=time_lookup[time_period]))
    return _browse_song(annotation, limit)


# -------------------------------------
# trending albums

def trending_albums(time_period, limit=_DEFAULT_LIMIT):
    assert time_period in time_lookup.keys(), f"Could not find 'time_period' value '{time_period}' in lookup."
    annotation = Count('song__streams__id', filter=Q(song__streams__timestamp__gte=time_lookup[time_period]))
    return _browse_album(annotation, limit)
