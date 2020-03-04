"""
Created:04 Mar. 2020
Author: Jordan Prechac
"""

from revibe._helpers import const

from content.models import Song, Album, Artist
from content.serializers import v1 as cnt_ser_v1

# -----------------------------------------------------------------------------

_DEFAULT_LIMIT = 25
_name = "name"
_type = "type"
_results = "results"

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