"""
Author: Jordan Prechac
Created: 26 Feb. 2020
"""

from django.db.models import Count, Q

import datetime

from revibe._helpers import const

from content.models import Song, Album, Artist
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


# -----------------------------------------------------------------------------
# utils

def _browse_song(annotation, limit=_DEFAULT_LIMIT):
    songs = Song.display_objects.filter(platform=const.REVIBE_STRING).annotate(count=annotation).order_by('-count')[:limit]
    return cnt_ser_v1.SongSerializer(songs, many=True)

def _browse_album(annotation, limit=_DEFAULT_LIMIT):
    albums = Album.display_objects.filter(platform=const.REVIBE_STRING).annotate(count=annotation).order_by('-count')[:limit]
    return cnt_ser_v1.AlbumSerializer(albums, many=True)

def _browse_artist(annotation, limit=_DEFAULT_LIMIT):
    artists = Artist.objects.filter(platform=const.REVIBE_STRING).annotate(count=annotation).order_by('-count')[:limit]
    return cnt_ser_v1.ArtistSerializer(artists, many=True)

# -----------------------------------------------------------------------------
##### all-time #####

# -------------------------------------
# top songs

def top_songs_all_time(limit=_DEFAULT_LIMIT):
    """
    Retrieve the top played songs on Revibe of all-time
    """
    annotation = Count('streams__id')
    return _browse_song(annotation, limit)


# -------------------------------------
# top albums

def top_albums_all_time(limit=_DEFAULT_LIMIT):
    """
    Retrieve the top played albums on Revibe of all-time
    """
    annotation = Count('song__streams__id')
    return _browse_album(annotation, limit)


# -------------------------------------
# top artists

def top_artists_all_time(limit=_DEFAULT_LIMIT):
    """
    """
    annotation = Count('song_uploaded_by__streams__id')
    return _browse_artist(annotation, limit)


# -----------------------------------------------------------------------------
##### trending #####

def trending_songs(time_period, limit=_DEFAULT_LIMIT):
    assert time_period in time_lookup.keys(), f"Could not find 'time_period' value '{time_period}' in lookup."
    annotation = Count('streams__id', filter=Q(streams__timestamp__gte=time_lookup[time_period]))
    return _browse_song(annotation, limit)

def trending_albums(time_period, limit=_DEFAULT_LIMIT):
    assert time_period in time_lookup.keys(), f"Could not find 'time_period' value '{time_period}' in lookup."
    annotation = Count('song__streams__id', filter=Q(song__streams__timestamp__gte=time_lookup[time_period]))
    return _browse_album(annotation, limit)

def trending_artists(time_period, limit=_DEFAULT_LIMIT):
    assert time_period in time_lookup.keys(), f"Could not find 'time_period' value '{time_period}' in lookup."
    annotation = Count('song_uploaded_by__streams__id', filter=Q(song_uploaded_by__streams__timestamp__gte=time_lookup[time_period]))
    return _browse_artist(annotation, limit)


# -----------------------------------------------------------------------------

time_options = [
    ("today", "Today"),
    ("last_week", "This Week"),
    ("last_month", "This Month"),
]
trending_options = [
    {
        "function": trending_songs,
        "name": "{}'s Trending Songs",
        "type": "songs"
    },
    {
        "function": trending_albums,
        "name": "{}'s Trending Albums",
        "type": "albums"
    },
    {
        "function": trending_artists,
        "name": "{}'s Trending Artists",
        "type": "artists"
    }
]

all_browse_options = [
    {
        "function": top_songs_all_time,
        "name": "Revibe's Top Songs",
        "type": "songs"
    },
    {
        "function": top_albums_all_time,
        "name": "Revibe's Top Albums",
        "type": "albums"
    },
    {
        "function": top_artists_all_time,
        "name": "Revibe's Top Artists",
        "type": "artists"
    },
    # {
    #     "function": trending_songs,
    #     "name": "Today's Trending Songs",
    #     "type": "songs",
    #     "params": {"time_period": "today"}
    # },
    # {
    #     "function": trending_albums,
    #     "name": "This Month's Trending Songs",
    #     "type": "albums",
    #     "params": {"time_period": "last_month"}
    # },
    # {
    #     "function": trending_artists,
    #     "name": "This Week's Trending Artists",
    #     "type": "artists",
    #     "params": {"time_period": "last_week"}
    # }
]
for i in trending_options:
    for j in time_options:
        all_browse_options.append({
            "function": i["function"],
            "name": i["name"].format(j[1]),
            "type": i["type"],
            "params": {"time_period": j[0]}
        })