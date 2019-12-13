from music.models import *

RevibeArtists = Artist.objects \
    .filter(platform="Revibe")

RevibeAlbums = Album.objects \
    .filter(platform="Revibe")

RevibeSongs = Song.objects \
    .filter(platform="Revibe")

RevibeHiddenAlbums = Album.all_objects \
    .filter(platform="Revibe")

RevibeHiddenSongs = Song.all_objects \
    .filter(platform="Revibe")
