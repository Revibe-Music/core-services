from .models import *
from . import mixins
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

class BaseAlbumSerializer(serializers.ModelSerializer, mixins.ImageURLMixin):
    contributions = als.AlbumContributorSerializer(many=True, source='album_to_artist')
    class Meta:
        model = Album
        fields = [
            'id',
            'name',
            'image',
            'platform',
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

class BaseAlbumContributorSerializer(serializers.ModelSerializer):
    artist = BaseArtistSerializer(many=False)
    album = BaseAlbumSerializer(many=False)
    class Meta:
        model = AlbumContributor
        fields = [
            'artist',
            'album',
            'contribution_type'
        ]

class BaseSongContributorSerialzer(serializers.ModelSerializer):
    artist = BaseArtistSerializer(many=False)
    song = BaseSongSerializer(many=False)
    class Meta:
        model = SongContributor
        fields = [
            'artist',
            'song',
            'contribution_type'
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
