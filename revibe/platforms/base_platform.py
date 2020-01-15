from django.core.exceptions import MultipleObjectsReturned, ObjectDoesNotExist

from revibe._errors import random as errors, platforms as plt_er, data as data_err
from revibe._helpers import const

from content.models import *
from content.serializers import v1 as content_ser_v1
from music.models import *
from music.serializers import v1 as music_ser_v1

# -----------------------------------------------------------------------------

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
            self.ArtistSerializer = content_ser_v1.OtherArtistSerializer
            self.AlbumSerializer = content_ser_v1.OtherAlbumSerializer
            self.SongSerializer = content_ser_v1.OtherSongSerializer

    def _invalidate_revibe(self):
        if self.__str__() == const.REVIBE_STRING:
            raise NotImplementedError("Class '{}' must define this method".format(self.__str__()))

    def _save_artist(self, data, *args, **kwargs):
        self._invalidate_revibe()

        # validate data
        if 'artist' in data.keys():
            data = data['artist']

        data['platform'] = self.__str__()
        serializer = self.ArtistSerializer(data=data, *args, **kwargs)
        good = True
        if serializer.is_valid():
            instance = serializer.save()
            return instance
        else:
            raise data.SerializerValidationError(detail=serializer.errors)

    def get_artist(self, data, *args, **kwargs):
        """
        Tries to get the artist with this ID, otherwise creates the artist
        """
        # validate data
        if 'artist' in data.keys():
            data = data['artist']

        artists = Artist.objects.filter(id=data['artist_id'])
        num_returned = artists.count()
        if num_returned == 1:
            artist = artists[0]
            if artist.platform != self.__class__.__name__:
                raise plt_er.InvalidPlatformContent("The content found's platform does not match the expected platform")
            return artist
        
        elif num_returned > 1:
            raise plt_er.InvalidPlatformContent("Found multiple artists with this ID")

        else: #can only be 0 now
            return self._save_artist(data)

    def _save_album(self, data, artist, *args, **kwargs):
        self._invalidate_revibe()

        # validate data
        if 'album' in data.keys():
            data = data['album']

        data['platform'] = self.__str__()
        serializer = self.AlbumSerializer(data=data, *args, **kwargs)
        good = True
        if serializer.is_valid():
            instance = serializer.save()
            instance.uploaded_by = artist
            instance.save()
            return instance
        else:
            raise data.SerializerValidationError(detail=serializer.errors)
    
    def get_album(self, data, artist, *args, **kwargs):
        """
        Tries to get an album based on the ID, otherwise creates an Album
        """
        # validate data
        if 'album' in data.keys():
            data = data['album']
        
        albums = Album.objects.filter(id=data['album_id'])
        num_returned = albums.count()

        if num_returned == 1:
            album = albums[0]
            if not album.platform == self.__class__.__name__:
                raise plt_er.InvalidPlatformContent("The content found's platform does not match the expected platform")
            return album

        elif num_returned > 1:
            raise plt.InvalidPlatformContent("Found multiple artists with this ID")
        
        else: # can only be 0
            return self._save_album(data, artist, *args, **kwargs)

    def _save_song(self, data, artist, album, *args, **kwargs):
        self._invalidate_revibe()
        data['platform'] = self.__str__()
        data['album_id'] = str(album.id)
        data['artist_id'] = str(artist.id)
        serializer = self.SongSerializer(data=data, *args, **kwargs)
        if serializer.is_valid():
            instance = serializer.save()
            return instance
        else:
            raise data_err.SerializerValidationError(detail=serializer.errors)
    
    def get_song(self, data, artist, album, *args, **kwargs):
        """
        Tries to get the song based on the ID, otherwise creates the Song
        """
        # validate data
        if 'song' in data.keys():
            data = data['song']
        
        songs = Song.objects.filter(id=data['song_id'])
        num_returned = songs.count()

        if num_returned == 1:
            song = songs[0]
            if song.platform != self.__class__.__name__:
                raise plt_er.InvalidPlatformContent("The content found's platform does not match the expected platform")
            return song
        
        elif num_returned > 1:
            raise plt.InvalidPlatformContent("Found multiple artists with this ID")

        else: #can only be 0
            return self._save_song(data, artist, album, *args, **kwargs)

    def _validate_save_data(self, data):
        errs = {}
        required_dicts = ['song','album','artist']
        for dic in required_dicts:
            if dic not in data.keys():
                errs[dic] = ["when saving non-revibe content, must include a '{}' object".format(dic)]

    def save(self, data, *args, **kwargs):
        """
        Expecting data to look like:
        {
            "artist": {
                "artist_id": "...",
                "artist_uri": ...,
                "name": ...,
                "image_ref": ...
                ...
            },
            "album": {
                "album_id": ...,
                "album_uri": ...,
                "name": ...,
                "image_ref": ...,
                ...
            },
            "song": {
                "song_id": "...",
                "song_uri": ...,
                "title": ...,
                "duration": ...,
                ...
            }
        }
        """
        self._invalidate_revibe()
        self._validate_save_data(data)

        artist_data = data.pop('artist')
        album_data = data.pop('album')
        song_data = data.pop('song')

        artist = self.get_artist(artist_data, *args, **kwargs)
        album = self.get_album(album_data, artist, *args, **kwargs)
        song = self.get_song(song_data, artist, album, *args, **kwargs)

        return song

    def save_song_to_library(self, request, *args, **kwargs):
        """
        Saves a song to a user's library
        """
        user = request.user
        data = request.data
        
        try:
            library = Library.objects.get(user=user, platform=self.__class__.__name__)
        except Library.DoesNotExist as e:
            raise plt_er.PlatformNotFoundError("This user does not have a {} library".format(self.__class__.__name__))

        song = self.save(data, *args, **kwargs)

        instance = LibrarySong.objects.create(library=library, song=song)
        instance.save()

        return instance

