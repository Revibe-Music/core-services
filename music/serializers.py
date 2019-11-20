from music.models import *
from music import mixins
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
    contributions = als.AlbumContributorSerializer(many=True, source='album_to_artist')
    image = serializers.SerializerMethodField('get_image_url')
    class Meta:
        model = Album
        fields = [
            'id',
            'name',
            'image',
            'platform',
            'type',
            'contributions',
        ]

class BaseSongSerializer(serializers.ModelSerializer):
    """
    Base of the rest of the song serializers in the API.

    The base is considered what is shown in the library list (app landing page)
    """
    contributions = ss.SongContributorSerializer(many=True, source='song_to_artist')
    album = ss.SongAlbumSerializer(many=False)

    class Meta:
        model = Song
        fields = [
            'id',
            'uri',
            'title',
            'duration',
            'platform',
            'album',
            'contributions',
        ]

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

# class BaseSongContributorSerialzer(serializers.ModelSerializer):
#     artist = BaseArtistSerializer(many=False)
#     song = BaseSongSerializer(many=False)
#     class Meta:
#         model = SongContributor
#         fields = [
#             'artist',
#             'song',
#             'contribution_type'
#         ]

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
            'date_saved'
        ]
class BasePlaylistSongSerializer(serializers.ModelSerializer):
    class Meta:
        model = PlaylistSongs
        fields = [
            'playlist',
            'song',
            'date_saved'
        ]
