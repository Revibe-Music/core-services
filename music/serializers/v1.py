from django.shortcuts import get_object_or_404
from rest_framework import serializers

import logging
logger = logging.getLogger(__name__)

from revibe._errors import auth, data, network
from revibe._helpers.debug import debug_print

from accounts.models import ArtistProfile
from content.models import *
from content.serializers.v1 import *
from music.models import *

# -----------------------------------------------------------------------------

class LibrarySerializer(serializers.ModelSerializer):
    platform = serializers.CharField(read_only=True)
    # songs = SongSerializer(many=True, read_only=True)
    class Meta:
        model = Library
        fields = [
            'id',
            'platform',
            # 'songs',
        ]


class PlaylistSerializer(serializers.ModelSerializer):

    description = serializers.CharField(required=False)

    # read-only
    curated = serializers.BooleanField(source='revibe_curated', read_only=True)
    # songs = SongSerializer(many=True, read_only=True)

    # write-only fields

    class Meta:
        model = Playlist
        fields = [
            'id',
            'name',
            'description',
            'curated',
            'date_created',
            # 'songs',
        ]
    
    def get_user(self):
        request = self.context.get("request")
        user = request.user
        if user is None:
            raise auth.NoAuthenticationError("Could not identify the current user")
        return user
    
    def create(self, validated_data, *args, **kwargs):
        user = self.get_user()

        name = validated_data['name']

        # check that this user does not have a playlist with this name already
        check = Playlist.objects.filter(name=name, user=user)
        if len(check) == 1:
            raise network.ConflictError("A playlist with this name already exists") # 409 error
        if len(check) > 1:
            raise data.TooManyObjectsReturnedError() # 512

        # create the playlist
        playlist = Playlist.objects.create(user=user, **validated_data)
        playlist.save()
        return playlist


class ReadOnlyLibrarySongSerializer(serializers.ModelSerializer):
    song = SongSerializer(read_only=True)

    class Meta:
        model = LibrarySong
        fields = [
            "song",
            "date_saved",
        ]


class LibrarySongSerializer(serializers.ModelSerializer):
    # read-only fields
    library = serializers.ReadOnlyField(source='library.id')
    song = SongSerializer(read_only=True)
    # write-only fields
    song_id = serializers.CharField(write_only=True)
    class Meta:
        model = LibrarySong
        fields = [
            'library',
            'song',
            'date_saved',
            # write-only fields
            'song_id',
        ]

    def get_library(self, platform):
        """
        Gets the library of the current request's user d on the platform passed
        """
        request = self.context.get("request")
        user = request.user

        libraries = Library.objects.filter(platform=platform, user=user)
        if len(libraries) != 1:
            raise serializers.ValidationError("Error retrieving user's {} library".format(platform))
        
        library = libraries[0]
        
        return library
    
    def create(self, validated_data):
        # get song
        song = get_object_or_404(Song.objects.all(), pk=validated_data["song_id"])
        platform = song.platform

        library = self.get_library(platform)

        # make sure the song hasn't already been added
        check = LibrarySong.objects.filter(library=library, song=song)
        if len(check) == 1:
            return check[0]
        elif len(check) > 1:
            raise serializers.ValidationError("Error saving song to library: multiple songs found with this ID.")

        # save the song to that library
        lib_song = LibrarySong.objects.create(library=library, song=song)
        
        return lib_song
    
    def delete(self, data):
        # assert data['song_id'], "'song_id' must be passed with this endpoint"
        if 'song_id' not in data.keys():
            raise network.BadRequestError("Field 'song_id' is required")

        # get the current song
        song = get_object_or_404(Song.objects.all(), pk=data["song_id"])
        platform = song.platform
        if settings.DEBUG:
            print(song)
        
        library = self.get_library(platform)

        try:
            lib_song = LibrarySong.objects.get(library=library, song=song)
            lib_song.delete()
        except LibrarySong.DoesNotExist:
            logger.debug(f"Could not find LibrarySong. Library: {library}. Song: {song}")



class PlaylistSongSerializer(serializers.ModelSerializer):
    order = serializers.IntegerField(required=False)
    # read-only fields
    playlist = serializers.ReadOnlyField(source='playlist.id')
    song = SongSerializer(read_only=True)
    # write-only fields
    song_id = serializers.CharField(write_only=True)
    playlist_id = serializers.IntegerField(write_only=True)
    class Meta:
        model = PlaylistSong
        fields = [
            'playlist',
            'song',
            'date_saved',
            'order',
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

        song_id = validated_data.pop('song_id', None)
        playlist_id = validated_data.pop("playlist_id", None)
        user_playlists = Playlist.objects.filter(user=user)
        if len(user_playlists) == 0:
            raise network.BadRequestError("The user has not playlists")

        # some custom 'get_song()' method to check if non-revibe songs are saved in the DB

        song = get_object_or_404(Song.objects.all(), pk=song_id) # needs to be changed later to save other platform's songs
        playlist = get_object_or_404(user_playlists, pk=playlist_id)
        
        if song in playlist.songs.all():
            return data.ObjectAlreadyExists("{} is already in playlist {}".format(song.title, playlist.name))

        print(validated_data)
        ps = PlaylistSong.objects.create(playlist=playlist, song=song, **validated_data)
        ps.save()

        return ps
    
    def delete(self, data, *args, **kwargs):
        assert data['song_id'], "'song_id' must be passed in this endpoint"
        assert data['playlist_id'], "'playlist_id' must be passed in this endpoint"

        user = self.get_user()

        song = get_object_or_404(Song.objects.all(), pk=data['song_id'])
        playlist = get_object_or_404(Playlist.objects.filter(user=user), pk=data['playlist_id'])

        ps = PlaylistSong.objects.filter(playlist=playlist, song=song)
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

