"""
Author: Jordan Prechac
Created: 26 Feb. 2020
"""

from django.db.models import Count

from content.models import Song, Album
from content.serializers import v1 as cnt_ser_v1
from metrics.models import Stream

# -----------------------------------------------------------------------------

_DEFAULT_LIMIT = 25

def top_songs_all_time(limit=_DEFAULT_LIMIT):
    """
    Retrieve the top played songs on Revibe of all-time

    Takes no required arguments, can override the limit if desired.

    Must ALWAYS return a SongSerializer object.
    """
    songs = Song.display_objects.annotate(count=Count('streams__id')).order_by('-count')[:limit]
    serializer = cnt_ser_v1.SongSerializer(songs, many=True)
    return serializer

def top_albums_all_time(limit=_DEFAULT_LIMIT):
    """
    Retrieve the top played albums on Revibe of all-time

    Takes no required arguments, can override the limit if desired.

    Must ALWAYS return an AlbumSerializer object.
    """
    albums = Album.display_objects.annotate(count=Count('song__streams__id')).order_by('count')[:limit]
    serializer = cnt_ser_v1.AlbumSerializer(albums, many=True)
    return serializer
