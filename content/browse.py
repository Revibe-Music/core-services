"""
Author: Jordan Prechac
Created: 26 Feb. 2020
"""

from django.db.models import (
    Count, Expression, F, Q,
    # fields
    IntegerField
)
from django.db.models.functions import ExtractDay

import datetime

from revibe._helpers import const

from administration.utils.models import todays_artist_spotlight
from content.models import Song, Album, Artist
from content.serializers import v1 as cnt_ser_v1
from metrics.models import Stream

# -----------------------------------------------------------------------------

_DEFAULT_LIMIT = 25
_name = "name"
_type = "type"
_results = "results"

today = datetime.datetime.now()
yesterday = today - datetime.timedelta(days=1)
last_week = today - datetime.timedelta(days=7)
last_month = today - datetime.timedelta(days=30)

time_lookup = {
    "today": yesterday, # this naming makes it easier for person making the request. Essentially it's songs popular within the last 24 hours
    "last_week": last_week,
    "last_month": last_month,
}
time_names = {
    "today": "Today",
    "last_week": "This Week",
    "last_month": "This Month",
}


# -----------------------------------------------------------------------------
# utils

def _browse_song(annotation, limit=_DEFAULT_LIMIT, platform=const.REVIBE_STRING, **options):
    songs = Song.display_objects.filter(platform=platform).annotate(count=annotation).order_by('-count')[:limit]
    options[_results] = cnt_ser_v1.SongSerializer(songs, many=True).data

    return options

def _browse_album(annotation, limit=_DEFAULT_LIMIT, **options):
    albums = Album.display_objects.filter(platform=const.REVIBE_STRING).annotate(count=annotation).order_by('-count')[:limit]
    options[_results] = cnt_ser_v1.AlbumSerializer(albums, many=True).data

    return options

def _browse_artist(annotation, limit=_DEFAULT_LIMIT, **options):
    artists = Artist.objects.filter(platform=const.REVIBE_STRING).annotate(count=annotation).order_by('-count')[:limit]
    options[_results] = cnt_ser_v1.ArtistSerializer(artists, many=True).data

    return options

# -----------------------------------------------------------------------------
##### all-time #####

def top_songs_all_time(limit=_DEFAULT_LIMIT):
    """
    Retrieve the top played songs on Revibe of all-time
    """
    annotation = Count('streams__id')

    options = {
        _name: "Top Songs",
        _type: "songs"
    }

    return _browse_song(annotation, limit, **options)

def top_albums_all_time(limit=_DEFAULT_LIMIT):
    """
    Retrieve the top played albums on Revibe of all-time
    """
    annotation = Count('song__streams__id')

    options = {
        _name: "Top Albums",
        _type: "albums"
    }

    return _browse_album(annotation, limit, **options)

def top_artists_all_time(limit=_DEFAULT_LIMIT):
    """
    """
    annotation = Count('song_uploaded_by__streams__id')

    options = {
        _name: "Top Artists",
        _type: "artists"
    }

    return _browse_artist(annotation, limit, **options)


# -----------------------------------------------------------------------------
##### trending #####

def trending_songs(time_period, limit=_DEFAULT_LIMIT):
    assert time_period in time_lookup.keys(), f"Could not find 'time_period' value '{time_period}' in lookup."
    annotation = Count('streams__id', filter=Q(streams__timestamp__gte=time_lookup[time_period]))

    options = {
        _name: "Trending Songs",
        _type: "songs"
    }

    return _browse_song(annotation, limit, **options)

def trending_albums(time_period, limit=_DEFAULT_LIMIT):
    assert time_period in time_lookup.keys(), f"Could not find 'time_period' value '{time_period}' in lookup."
    annotation = Count('song__streams__id', filter=Q(song__streams__timestamp__gte=time_lookup[time_period]))

    options = {
        _name: "Trending Albums",
        _type: "albums"
    }

    return _browse_album(annotation, limit, **options)

def trending_artists(time_period, limit=_DEFAULT_LIMIT):
    assert time_period in time_lookup.keys(), f"Could not find 'time_period' value '{time_period}' in lookup."
    annotation = Count('song_uploaded_by__streams__id', filter=Q(song_uploaded_by__streams__timestamp__gte=time_lookup[time_period]))

    options = {
        _name: "Trending Artists",
        _type: "artists"
    }

    return _browse_artist(annotation, limit, **options)

def treding_youtube_videos(time_period, limit=_DEFAULT_LIMIT):
    """
    Similar to the 
    """
    assert time_period in time_lookup.keys(), f"Coulf not find 'time_period' value '{time_period}' in lookup"
    annotation = Count('streams__id', filter=Q(streams__timestamp__gte=time_lookup[time_period]))

    options = {
        _name: "Popular on Revibe",
        _type: "songs",
    }

    return _browse_song(annotation, limit, platform=const.YOUTUBE_STRING, **options)


# -----------------------------------------------------------------------------
##### recently uploaded #####

def recently_uploaded_albums(time_period="last_week", limit=_DEFAULT_LIMIT):
    assert time_period in time_lookup.keys(), f"Could not find 'time_period' value '{time_period}' in lookup."
    
    # get the albums uploaded this week
    number_of_streams = Count("song__streams__id", filter=Q(song__streams__timestamp__gte=time_lookup[time_period]))
    albums = Album.display_objects.filter(
            # filter for only Revibe albums published in the last <time_period>
            platform=const.REVIBE_STRING,
            date_published__gte=time_lookup[time_period]
        ).annotate(
            # divide the number of streams by the number of days it's been out
            number_of_streams=number_of_streams,
            days_since_publish=Expression(datetime.datetime.now().date() - F('date_published'))
        ).annotate(
            number_of_streams_per_day=F('number_of_streams') / F('days_since_publish')
        ).order_by('-number_of_streams_per_day')[:limit]
    
    return cnt_ser_v1.AlbumSerializer(albums, many=True)


# -----------------------------------------------------------------------------
##### other #####

def artist_spotlight():
    artist = todays_artist_spotlight()

    options = {
        _name: "Artist Spotlight",
        _type: "artist",
        _results: cnt_ser_v1.ArtistSerializer(artist, many=False).data if artist != None else None
    }

    return options

