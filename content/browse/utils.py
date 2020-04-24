"""
Created:04 Mar. 2020
Author: Jordan Prechac
"""

from revibe._helpers import const

from administration.utils import retrieve_variable
from content.models import Song, Album, Artist
from content.serializers import v1 as cnt_ser_v1

# -----------------------------------------------------------------------------

# _DEFAULT_LIMIT = 50
# limit_variable = retrieve_variable()
# try:
#     limit_variable = int(limit_variable)
#     _DEFAULT_LIMIT = max(min(limit_variable, 100), 10)
# except ValueError as ve:
#     print("Could not read browse section default limit variable")
#     print(ve)
def _DEFAULT_LIMIT():
    limit_variable = retrieve_variable("browse_section_default_limit", 50)

    try:
        limit_variable = int(limit_variable)
        return max(min(limit_variable, 100), 10)
    except ValueError as ve:
        print("Could not read browse section default limit variable")
        print(ve)
    
    return 50

_name = "name"
_type = "type"
_results = "results"
_endpoint = "endpoint"

def _browse_song(annotation, limit=None, platform=const.REVIBE_STRING, **options):
    limit = limit if limit else _DEFAULT_LIMIT()
    songs = Song.display_objects.filter(platform=platform).annotate(count=annotation).order_by('-count')[:limit]
    options[_results] = cnt_ser_v1.SongSerializer(songs, many=True).data

    return options

def _browse_album(annotation, limit=None, **options):
    limit = limit if limit else _DEFAULT_LIMIT()
    albums = Album.display_objects.filter(platform=const.REVIBE_STRING).annotate(count=annotation).order_by('-count')[:limit]
    options[_results] = cnt_ser_v1.AlbumSerializer(albums, many=True).data

    return options

def _browse_artist(annotation, limit=None, **options):
    limit = limit if limit else _DEFAULT_LIMIT()
    artists = Artist.display_objects.filter(platform=const.REVIBE_STRING).annotate(count=annotation).order_by('-count')[:limit]
    options[_results] = cnt_ser_v1.ArtistSerializer(artists, many=True).data

    return options