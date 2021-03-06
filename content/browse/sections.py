"""
Author: Jordan Prechac
Created: 26 Feb. 2020
"""

from django.db.models import (
    Count, ExpressionWrapper, F, Q,
    # fields
    IntegerField, CharField, DecimalField
)
from django.db.models.functions import ExtractDay
from django.urls import reverse


import datetime

from revibe._helpers import const
from revibe.contrib.queries.functions import Day, Month, Year

from .utils import (
    _browse_song, _browse_album, _browse_artist,
    _DEFAULT_LIMIT, _name, _type, _results, _endpoint
)

from administration.utils.models import todays_artist_spotlight
from content.models import Song, Album, Artist
from content.serializers import v1 as cnt_ser_v1
from metrics.models import Stream
from music.models import Playlist
from music.serializers import v1 as msc_ser_v1

# -----------------------------------------------------------------------------


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
##### all-time #####

def top_songs_all_time(limit=None, **kwargs):
    """
    Retrieve the top played songs on Revibe of all-time
    """
    limit = limit if limit else _DEFAULT_LIMIT()

    annotation = Count('streams__id')

    options = {
        _name: "Top Songs",
        _type: "songs",
        _endpoint: "browse/top-songs-all-time/"
    }

    return _browse_song(annotation, limit, **options)

def top_albums_all_time(limit=None, **kwargs):
    """
    Retrieve the top played albums on Revibe of all-time
    """
    limit = limit if limit else _DEFAULT_LIMIT()
    annotation = Count('song__streams__id')

    options = {
        _name: "Top Albums",
        _type: "albums",
        _endpoint: "browse/top-albums-all-time/"
    }

    return _browse_album(annotation, limit, **options)

def top_artists_all_time(limit=None, **kwargs):
    """
    """
    limit = limit if limit else _DEFAULT_LIMIT()
    annotation = Count('song_uploaded_by__streams__id')

    options = {
        _name: "Top Artists",
        _type: "artists",
        _endpoint: "browse/top-artists-all-time/"
    }

    return _browse_artist(annotation, limit, **options)


# -----------------------------------------------------------------------------
##### trending #####

def trending_songs(time_period="last_week", limit=None, **kwargs):
    assert time_period in time_lookup.keys(), f"Could not find 'time_period' value '{time_period}' in lookup."
    limit = limit if limit else _DEFAULT_LIMIT()
    annotation = Count('streams__id', filter=Q(streams__timestamp__gte=time_lookup[time_period]))

    options = {
        _name: "Trending Songs",
        _type: "songs",
        _endpoint: "browse/trending-songs/"
    }

    return _browse_song(annotation, limit, **options)

def trending_albums(time_period="last_week", limit=None, **kwargs):
    assert time_period in time_lookup.keys(), f"Could not find 'time_period' value '{time_period}' in lookup."
    limit = limit if limit else _DEFAULT_LIMIT()
    annotation = Count('song__streams__id', filter=Q(song__streams__timestamp__gte=time_lookup[time_period]))

    options = {
        _name: "Trending Albums",
        _type: "albums",
        _endpoint: "browse/trending-albums/",
    }

    return _browse_album(annotation, limit, **options)

def trending_artists(time_period="last_week", limit=None, **kwargs):
    assert time_period in time_lookup.keys(), f"Could not find 'time_period' value '{time_period}' in lookup."
    limit = limit if limit else _DEFAULT_LIMIT()
    annotation = Count('song_uploaded_by__streams__id', filter=Q(song_uploaded_by__streams__timestamp__gte=time_lookup[time_period]))

    options = {
        _name: "Trending Artists",
        _type: "artists",
        _endpoint: "browse/trending-artists/",
    }

    return _browse_artist(annotation, limit, **options)

def trending_youtube(time_period="last_week", limit=None, **kwargs):
    """
    Similar to the 
    """
    assert time_period in time_lookup.keys(), f"Coulf not find 'time_period' value '{time_period}' in lookup"
    limit = limit if limit else _DEFAULT_LIMIT()
    annotation = Count('streams__id', filter=Q(streams__timestamp__gte=time_lookup[time_period]))

    options = {
        _name: "Popular on Revibe",
        _type: "songs",
        _endpoint: "browse/trending-youtube/",
    }

    return _browse_song(annotation, limit, platform=const.YOUTUBE_STRING, **options)


# -----------------------------------------------------------------------------
##### recently uploaded #####

def recently_uploaded_albums(time_period="last_week", limit=None, **kwargs):
    assert time_period in time_lookup.keys(), f"Could not find 'time_period' value '{time_period}' in lookup."
    limit = limit if limit else _DEFAULT_LIMIT()

    # get the albums uploaded this week
    days_offset = 20198306 + 1 # the 20m whatever number is to counteract the weirdness of the datetime subtraction thing, and the 1 is to avoid dividing by 0
    number_of_streams = Count('song__streams__id', filter=Q(song__streams__timestamp__gte=time_lookup[time_period]))
    albums = Album.display_objects.filter(
            # filter for only Revibe albums published in the last <time_period>
            platform=const.REVIBE_STRING,
            date_published__gte=time_lookup[time_period]
        ).annotate(
            # divide the number of streams by the number of days it's been out
            count=number_of_streams,
            days_since_publish=ExpressionWrapper(datetime.datetime.now().date() - F('date_published') + days_offset, output_field=IntegerField())
        ).annotate(
            number_of_streams_per_day=ExpressionWrapper(F('count') / F('days_since_publish'), output_field=DecimalField())
        ).order_by('-number_of_streams_per_day')[:limit]
        # ).order_by('-count')[:limit]

    options = {
        _name: "Recently Uploaded Albums",
        _type: "albums",
        _endpoint: "browse/recently-uploaded-albums/",
        _results: cnt_ser_v1.AlbumSerializer(albums, many=True).data,
    }

    return options


# -----------------------------------------------------------------------------
##### other #####

def artist_spotlight(**kwargs):
    artist = todays_artist_spotlight()

    options = {
        _name: "Artist Spotlight",
        _type: "artist",
        _endpoint: "browse/artist-spotlight/",
        _results: cnt_ser_v1.ArtistSerializer(artist, many=False).data if artist != None else None
    }

    return options


def revibe_playlists(limit=None, **kwargs):
    limit = limit if limit else _DEFAULT_LIMIT()

    playlists = Playlist.objects.filter(
        revibe_curated=True,
        is_public=True,
        show_on_browse=True
    )[:limit]

    options = {
        _name: "Curated Playlists",
        _type: "playlists",
        _endpoint: "browse/revibe-playlists/",
        _results: msc_ser_v1.PlaylistSerializer(playlists, many=True).data
    }

    return options


def top_content_container(**kwargs):
    return {
        "name": "Top Hits - All-Time",
        "type": "container",
        "results": [
            {
                "name": "Top Songs",
                "type": "songs",
                "icon": None,
                "url": "browse/top-songs-all-time/",
            },
            {
                "name": "Top Albums",
                "type": "albums",
                "icon": None,
                "url": "browse/top-albums-all-time/",
            },
            {
                "name": "Top Artists",
                "type": "artists",
                "icon": None,
                "url": "browse/top-artists-all-time/",
            },
        ],
    }

