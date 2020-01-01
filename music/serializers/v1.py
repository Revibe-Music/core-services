from django.shortcuts import get_object_or_404
from rest_framework import serializers

from artist_portal._helpers.debug import debug_print
from accounts.models import ArtistProfile
from content.models import *
from content.serializers.v1 import *
from music.models import *


class LibrarySerializer(serializers.ModelSerializer):
    platform = serializers.CharField(read_only=True)
    songs = SongSerializer(many=True, read_only=True)
    class Meta:
        model = Library
        fields = [
            'platform',
            'songs',
        ]

class PlaylistSerializer(serializers.ModelSerializer):
    songs = SongSerializer(many=True, read_only=True)
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

class LibrarySongSerializer(serializers.ModelSerializer):
    # read-only fields
    library = serializers.ReadOnlyField(source='library.id')
    song = serializers.ReadOnlyField(source='song.id')
    # write-only fields
    song_id = serializers.CharField(write_only=True)
    class Meta:
        model = LibrarySong
        fields = [
            'library',
            'song',
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
        assert data['song_id'], "'song_id' must be passed with this endpoint"

        # get the current song
        song = get_object_or_404(Song.objects.all(), pk=data["song_id"])
        platform = song.platform
        if settings.DEBUG:
            print(song)
        
        library = self.get_library(platform)

        lib_song = LibrarySong.objects.filter(library=library, song=song)
        if len(lib_song) != 1:
            raise serializers.ValidationError("error retrieving song from library")
        lib_song = lib_song[0]

        lib_song.delete()

class PlaylistSongSerializer(serializers.ModelSerializer):
    # read-only fields
    playlist = serializers.ReadOnlyField(source='playlist.id')
    song = serializers.ReadOnlyField(source='song.id')
    # write-only fields
    song_id = serializers.CharField(write_only=True)
    playlist_id = serializers.IntegerField(write_only=True)
    class Meta:
        model = PlaylistSong
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
        
        if song in playlist.songs.all():
            return PlaylistSong.objects.filter(playlist=playlist, song=song)[0]

        ps = PlaylistSong.objects.create(playlist=playlist, song=song)
        ps.save()

        return ps
    
    def delete(self, data, *args, **kwargs):
        assert data['song_id'], "'song_id' must be passed in this endpoint"
        assert data['playlist_id'], "'playlist_id' must be passed in this endpoint"

        user = self.get_user()

        song = get_object_or_404(Song.objects.all(), pk=data['song_id'])
        playlist = get_object_or_404(Playlist.objects.filter(user=user), pk=data['playlist_id'])
        debug_print(song)
        debug_print(playlist)

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

