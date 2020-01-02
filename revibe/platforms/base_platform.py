from django.core.exceptions import MultipleObjectsReturned, ObjectDoesNotExist

from revibe._errors import random as errors, platforms as plt_er
from revibe._helpers import const
from content.models import *
from content.serializers import v1 as content_ser_v1
from music.models import *
from music.serializers import v1 as music_ser_v1

class Platform:

    def __init__(self, *args, **kwargs):
        if self.__class__.__name__ == 'Platform':
            raise plt_er.InvalidPlatformOperation("Cannot instantiate class 'Platform', can only create instances of a subclass")
        self._get_queries()
        self._get_serializers()

    def __str__(self):
        return self.__class__.__name__
    
    def __repr__(self):
        return "<class {}>".format(self.__class__.__name__)

    def _get_queries(self):
        p = self.__str__()
        self.Artists = Artist.objects.filter(platform=p)
        self.Albums = Album.display_objects.filter(platform=p)
        self.Songs = Song.display_objects.filter(platform=p)
        self.AlbumContributors = AlbumContributor.display_objects.filter(album__platform=p)
        self.SongContributors = SongContributor.display_objects.filter(song__platform=p)

        # Music queries

        if self.__str__() == 'Revibe':
            self.HiddenAlbums = Album.hidden_objects.filter(platform=p)
            self.HiddenSongs = Song.hidden_objects.filter(platform=p)
            self.HiddenAlbumContributions = AlbumContributor.hidden_objects.filter(album__platform=p)
            self.HiddenSongContributors = SongContributor.hidden_objects.filter(song__platform=p)
    
    def _get_serializers(self):
        if self.__str__() == const.REVIBE_STRING:
            # Content Serializers
            self.ArtistSerializer = content_ser_v1.ArtistSerializer
            self.AlbumSerializer = content_ser_v1.AlbumSerializer
            self.AlbumContributorSerializer = content_ser_v1.AlbumContributorSerializer
            self.SongSerializer = content_ser_v1.SongSerializer
            self.SongContributorSerializer = content_ser_v1.SongContributorSerializer

            # Music Serializers
            self.LibrarySerializer = music_ser_v1.LibrarySerializer
            self.PlaylistSerializer = music_ser_v1.PlaylistSerializer
            self.LibrarySongSerializer = music_ser_v1.LibrarySongSerializer
            self.PlaylistSongSerializer = music_ser_v1.PlaylistSongSerializer
        else:
            self.ArtistSerializer = ser_v1.OtherArtistSerializer
            self.AlbumSerializer = ser_v1.OtherAlbumSerializer
            self.SongSerializer = ser_v1.OtherSongSerializer

    def _invalidate_revibe(self):
        if self.__str__() == const.REVIBE_STRING:
            raise NotImplementedError("Class '{}' must define this method".format(self.__str__()))

    def save_artist(self, data, *args, **kwargs):
        self._invalidate_revibe()
        data['platform'] = self.__str__()
        serializer = self.ArtistSerializer(data=data, *args, **kwargs)
        good = True
        if serializer.is_valid():
            instance = serializer.save()
            return (serializer, instance)
        else:
            good = False

        return (serializer, instance) if good else (serializer, None)

    def save_album(self, data, artist, *args, **kwargs):
        self._invalidate_revibe()
        data['platform'] = self.__str__()
        serializer = self.AlbumSerializer(data=data, *args, **kwargs)
        good = True
        if serializer.is_valid():
            instance = serializer.save()
            instance.uploaded_by = artist
            return (serializer, instance)
        else:
            good = False
        
        return (serializer, instance) if good else (serializer, None)

    def save_song(self, data, artist, album, *args, **kwargs):
        self._invalidate_revibe()
        data['platform'] = self.__str__()
        serializer = self.SongSerializer(data=data, *args, **kwargs)
        good = True
        if serializer.is_valid():
            instance = serializer.save()
            instance.uploaded_by = artist
            instance.album = album
            return (serializer, instance)
        else:
            good = False

        return (serializer, instance) if good else (serializer, None)

    def save(self, data, *args, **kwargs):
        """
        Expecting data to look like:
        {
            "artist": {
                "artist_id": "...",
                ...
            },
            "album": {
                "album_id": "...",
                ...
            },
            "song": {
                "song_id": "...",
                ...
            }
        }
        """
        artist_data = data.pop('artist')
        album_data = data.pop('album')
        song_data = data.pop('song')

        _, artist = self.save_artist(artist_data)
        assert artist, "Error saving the artist"
        _, album = self.save_album(album_data, artist)
        assert album, "Error saving the album"
        _, song = self.save_song(song_data, artist, album)
        assert song, "Error saving the song"

        return song

