from .models import *
from . import mixins
from rest_framework import serializers


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
    class Meta:
        model = Album
        fields = [
            'id',
            'name',
            'image',
            'platform',
            'uploaded_by',
            'album_to_artist',
        ]

class BaseSongSerializer(serializers.ModelSerializer):
    class Meta:
        model = Song
        fields = [
            'id',
            'uri',
            'title',
            'genre',
            'duration',
            'platform',
            'uploaded_date',
            'album',
            'uploaded_by',
            'song_to_artist',
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
    class Meta:
        model = Library
        fields = ['platform','songs']

class BasePlaylistSerializer(serializers.ModelSerializer):
    class Meta:
        model = Playlist
        # TODO: set fields manually
        fields = '__all__'
