from music.models import *

RevibeArtists = Artist.objects \
    .filter(platform="Revibe")

RevibeAlbums = Album.objects \
    .filter(platform="Revibe") \
    .filter(is_displayed=True) \
    .filter(is_deleted=False)

RevibeSongs = Song.objects \
    .filter(platform="Revibe") \
    .filter(is_displayed=True) \
    .filter(is_deleted=False)

