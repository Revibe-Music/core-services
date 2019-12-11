from artist_portal._helpers.debug import debug_print
from music.models import *
from music import mixins
from django.shortcuts import get_object_or_404
from rest_framework import serializers
from music.serializers._services import (
    song_serializers as ss,
    album_serializers as als
)


class BaseArtistSerializer(serializers.ModelSerializer, mixins.ImageURLMixin):
    class Meta:
        model = Artist
        fields = [
            'id',
            'name',
            'image',
            'platform'
        ]

class BaseAlbumSerializer(serializers.ModelSerializer,mixins.ImageURLMixin):
    contributions = als.AlbumContributorSerializer(many=True, source='album_to_artist', read_only=True)
    image = serializers.SerializerMethodField('get_image_url', read_only=True)
    image_up = serializers.FileField(source='image', write_only=True, allow_null=True)
    class Meta:
        model = Album
        fields = [
            'id',
            'name',
            'image',
            'image_up',
            'platform',
            'type',
            'contributions',
        ]
    
    def create(self, validated_data):
        # get the current user - the uploading artist ... ?
        artist = None
        request = self.context.get("request")
        if request and hasattr(request, "user"):
            artist = request.user.artist
        
        # create and save the album
        album = Album.objects.create(**validated_data, uploaded_by=artist)
        album.save()

        # create and save the default Album Contributors
        album_contrib = AlbumContributor.objects.create(artist=artist, album=album, contribution_type="Artist")
        album_contrib.save()

        return album

class BaseSongSerializer(serializers.ModelSerializer):
    """
    Base of the rest of the song serializers in the API.

    The base is considered what is shown in the library list (app landing page)
    """
    # read_only fields for displaying data
    contributions = ss.SongContributorSerializer(many=True, source='song_to_artist', read_only=True)
    album = ss.SongAlbumSerializer(many=False, read_only=True)

    # write_only fields for creating and updating songs
    album_id = serializers.CharField(source='album.id', write_only=True)
    song = serializers.FileField(source='file', write_only=True, allow_null=True)

    class Meta:
        model = Song
        fields = [
            'id',
            'uri',
            'title',
            'duration',
            'platform',
            'genre',
            'album',
            'contributions',
            # write-only fields
            'song',
            'album_id',
        ]
    
    def create(self, validated_data):
        """
        Function/endpoint for artists to upload their songs
        """
        # get the song's album from the provided ID
        album = validated_data.pop('album')
        album = get_object_or_404(Album.objects.all(), pk=album['id'])

        # get the current user
        artist = None
        request = self.context.get("request")
        if request and hasattr(request, "user"):
            artist = request.user.artist

        # create and save object to the database
        song = Song.objects.create(**validated_data, uploaded_by=artist, album=album)
        song.save()

        # add the uploading artist as a contributor to the SongContributor table
        song_contrib = SongContributor.objects.create(artist=artist, song=song, contribution_type="Artist")
        song_contrib.save()

        return song

class BaseAlbumContributorSerializer(serializers.ModelSerializer):
    """
    write-only serializer for creating, updating, and deleting
    album contributors
    """
    artist = serializers.CharField(source='artist.id', write_only=True)
    album = serializers.CharField(source='album.id', write_only=True)
    class Meta:
        model = AlbumContributor
        fields = [
            'id',
            'artist',
            'album',
            'contribution_type'
        ]

    def create(self, validated_data):
        # get artist and song data from validated_data
        artist = validated_data.pop('artist')
        artist = get_object_or_404(Artist.objects.all(), pk=artist['id'])
        album = validated_data.pop('album')
        album = get_object_or_404(Album.objects.all(), pk=album['id'])

        album_contrib = SongContributor.objects.create(**validated_data, artist=artist, song=song)
        album_contrib.save()
        return song_contrib

class AlbumAlbumContributorSerializer(serializers.ModelSerializer, mixins.AlbumImageURLMixin):
    album_id = serializers.ReadOnlyField(source='album.id')
    name = serializers.ReadOnlyField(source='album.name')
    image = serializers.SerializerMethodField('get_image_url')
    class Meta:
        model = AlbumContributor
        fields = [
            'id',
            'album_id',
            'name',
            'image',
            'contribution_type'
        ]
class ArtistAlbumContributorSerializer(serializers.ModelSerializer, mixins.ArtistImageURLMixin):
    artist_id = serializers.ReadOnlyField(source='artist.id')
    name = serializers.ReadOnlyField(source='artist.name')
    image = serializers.SerializerMethodField('get_image_url')
    class Meta:
        model = AlbumContributor
        fields = [
            'id',
            'artist_id',
            'name',
            'image',
            'contribution_type'
        ]

class BaseSongContributorSerialzer(serializers.ModelSerializer):
    artist = serializers.CharField(source='artist.id', write_only=True)
    song = serializers.CharField(source='song.id', write_only=True)
    class Meta:
        model = SongContributor
        fields = [
            'id',
            'artist',
            'song',
            'contribution_type'
        ]
    
    def list(self, request):
        pass
    def retrieve(self, request, pk=None):
        pass
    
    def create(self, validated_data):
        # get artist and song data from validated_data
        artist = validated_data.pop('artist')
        artist = get_object_or_404(Artist.objects.all(), pk=artist['id'])
        song = validated_data.pop('song')
        song = get_object_or_404(Song.objects.all(), pk=song['id'])

        song_contrib = SongContributor.objects.create(**validated_data, artist=artist, song=song)
        song_contrib.save()
        return song_contrib

class SongSongContributorSerializer(serializers.ModelSerializer):
    song_id = serializers.ReadOnlyField(source='song.id')
    uri = serializers.ReadOnlyField(source='song.uri')
    title = serializers.ReadOnlyField(source='song.title')
    duration = serializers.ReadOnlyField(source='song.duration')
    platform = serializers.ReadOnlyField(source='song.platform')
    album = ss.SongAlbumSerializer(many=False,source='song.album')
    contributions = ss.SongContributorSerializer(many=True, source='song.song_to_artist')
    class Meta:
        model = SongContributor
        fields = [
            'id',
            'song_id',
            'uri',
            'title',
            'duration',
            'platform',
            'album',
            'contributions',
            'contribution_type',
        ]

class BaseLibrarySerializer(serializers.ModelSerializer):
    songs = BaseSongSerializer(many=True)
    class Meta:
        model = Library
        fields = ['platform','songs']

class BasePlaylistSerializer(serializers.ModelSerializer):
    songs = BaseSongSerializer(many=True, read_only=True)
    # write-only fields
    class Meta:
        model = Playlist
        fields = [
            'id',
            'name',
            'songs',
        ]
    
    def get_user(self):
        request = self.context.get("request")
        user = request.user
        assert user is not None, "Could not identify the user."
        return user
    
    def create(self, validated_data, *args, **kwargs):
        user = self.get_user()

        if settings.DEBUG:
            print(validated_data)
        name = validated_data['name']

        # check that this user does not have a playlist with this name already
        check = Playlist.objects.filter(name=name, user=user)
        if len(check) == 1:
            raise serializers.ValidationError("A playlist with this name already exists")
        if len(check) > 1:
            raise serializers.ValidationError("Error retrieving playlist data")

        # create the playlist
        playlist = Playlist.objects.create(name=name, user=user)
        playlist.save()
        return playlist

class BaseLibrarySongSerializer(serializers.ModelSerializer):
    # read-only fields
    library = serializers.ReadOnlyField(source='library.id')
    song = serializers.ReadOnlyField(source='song.id')
    # write-only fields
    song_id = serializers.CharField(write_only=True)
    class Meta:
        model = LibrarySongs
        fields = [
            'library',
            'song',
            # write-only fields
            'song_id',
        ]
    
    def get_library(self, platform):
        """
        Gets the library of the current request's user based on the platform passed
        """
        request = self.context.get("request")
        user = request.user

        libraries = Library.objects.filter(platform=platform, user=user)
        if len(libraries) != 1:
            raise serializers.ValidationError("Error retrieving user's {} library".format(platform))
        
        library = libraries[0]
        if settings.DEBUG:
            print(library)
        
        return library
    
    def create(self, validated_data):
        # get song
        song = get_object_or_404(Song.objects.all(), pk=validated_data["song_id"])
        platform = song.platform
        if settings.DEBUG:
            print(song)

        library = self.get_library(platform)

        # make sure the song hasn't already been added
        check = LibrarySongs.objects.filter(library=library, song=song)
        if settings.DEBUG:
            print(check)
        if len(check) == 1:
            return check[0]
        elif len(check) > 1:
            raise serializers.ValidationError("Error saving song to library: multiple songs found with this ID.")

        # save the song to that library
        lib_song = LibrarySongs.objects.create(library=library, song=song)
        if settings.DEBUG:
            print(lib_song)
        
        return lib_song
    
    def delete(self, data):
        assert data['song_id'], "'song_id' must be passed with this endpoint"

        # get the current song
        song = get_object_or_404(Song.objects.all(), pk=data["song_id"])
        platform = song.platform
        if settings.DEBUG:
            print(song)
        
        library = self.get_library(platform)

        lib_song = LibrarySongs.objects.filter(library=library, song=song)
        if len(lib_song) != 1:
            raise serializers.ValidationError("error retrieving song from library")
        lib_song = lib_song[0]

        if settings.DEBUG:
            print(lib_song)
        
        lib_song.delete()

class BasePlaylistSongSerializer(serializers.ModelSerializer):
    # read-only fields
    playlist = serializers.ReadOnlyField(source='playlist.id')
    song = serializers.ReadOnlyField(source='song.id')
    # write-only fields
    song_id = serializers.CharField(write_only=True)
    playlist_id = serializers.IntegerField(write_only=True)
    class Meta:
        model = LibrarySongs
        fields = [
            'playlist',
            'song',
            # write-only fields
            'song_id',
            'playlist_id',
        ]
    
    def get_user(self):
        request = self.context.get("request")
        user = request.user
        assert user is not None, "Could not identify the user."
        return user
    
    def create(self, validated_data, *args, **kwargs):
        user = self.get_user()

        song_id = validated_data['song_id']
        playlist_id = validated_data["playlist_id"]
        user_playlists = Playlist.objects.filter(user=user)
        if len(user_playlists) == 0:
            raise serializers.ValidationError("Could not find user's playlists")

        song = get_object_or_404(Song.objects.all(), pk=song_id) # needs to be changed later to save other platform's songs
        playlist = get_object_or_404(user_playlists, pk=playlist_id)
        debug_print(song)
        debug_print(playlist)
        
        debug_print(playlist.songs.all())
        if song in playlist.songs.all():
            return PlaylistSongs.objects.filter(playlist=playlist, song=song)[0]

        ps = PlaylistSongs.objects.create(playlist=playlist, song=song)
        ps.save()
        debug_print(ps)

        return ps
    
    def delete(self, data, *args, **kwargs):
        assert data['song_id'], "'song_id' must be passed in this endpoint"
        assert data['playlist_id'], "'playlist_id' must be passed in this endpoint"

        user = self.get_user()

        song = get_object_or_404(Song.objects.all(), pk=data['song_id'])
        playlist = get_object_or_404(Playlist.objects.filter(user=user), pk=data['playlist_id'])
        debug_print(song)
        debug_print(playlist)

        ps = PlaylistSongs.objects.filter(playlist=playlist, song=song)
        debug_print(ps)
        if (len(ps) == 0) or (len(ps) > 1):
            raise serializers.ValidationError("Error finding song in playlist: found {} songs.".format(len(ps)))
        else:
            try:
                ps = ps[0]
            except TypeError:
                pass
            except Exception as e:
                raise e
        
        ps.delete()

