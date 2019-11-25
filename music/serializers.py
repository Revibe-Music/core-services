from music.models import *
from music import mixins
from django.shortcuts import get_object_or_404
from rest_framework import serializers
from .services import (
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
    image_up = serializers.FileField(source='image', write_only=True)
    # artist_id = serializers.UUIDField(source='uploaded_by.id', write_only=True)
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
            # 'artist_id',
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
    album_id = serializers.UUIDField(source='album.id', write_only=True)
    song = serializers.FileField(source='file', write_only=True)

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
            'song', # write only!
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
    artist = serializers.UUIDField(source='artist.id', write_only=True)
    album = serializers.UUIDField(source='album.id', write_only=True)
    class Meta:
        model = AlbumContributor
        fields = [
            'artist',
            'album',
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
        album = validated_data.pop('album')
        album = get_object_or_404(Album.objects.all(), pk=album['id'])

        album_contrib = SongContributor.objects.create(**validated_data, artist=artist, song=song)
        album_contrib.save()
        return song_contrib

class AlbumAlbumContributorSerializer(serializers.ModelSerializer, mixins.AlbumImageURLMixin):
    id = serializers.ReadOnlyField(source='album.id')
    name = serializers.ReadOnlyField(source='album.name')
    image = serializers.SerializerMethodField('get_image_url')
    class Meta:
        model = AlbumContributor
        fields = [
            'id',
            'name',
            'image',
            'contribution_type'
        ]
class ArtistAlbumContributorSerializer(serializers.ModelSerializer, mixins.ArtistImageURLMixin):
    id = serializers.ReadOnlyField(source='artist.id')
    name = serializers.ReadOnlyField(source='artist.name')
    image = serializers.SerializerMethodField('get_image_url')
    class Meta:
        model = AlbumContributor
        fields = [
            'id',
            'name',
            'image',
            'contribution_type'
        ]

class BaseSongContributorSerialzer(serializers.ModelSerializer):
    artist = serializers.UUIDField(source='artist.id', write_only=True)
    song = serializers.UUIDField(source='song.id', write_only=True)
    class Meta:
        model = SongContributor
        fields = [
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
    id = serializers.ReadOnlyField(source='song.id')
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
    class Meta:
        model = Playlist
        # TODO: set fields manually
        fields = '__all__'

class BaseLibrarySongSerializer(serializers.ModelSerializer):
    class Meta:
        model = LibrarySongs
        fields = [
            'library',
            'song',
        ]
class BasePlaylistSongSerializer(serializers.ModelSerializer):
    class Meta:
        model = PlaylistSongs
        fields = [
            'playlist',
            'song',
            'date_saved'
        ]