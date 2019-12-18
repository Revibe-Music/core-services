from rest_framework import serializers

from content.models import *


class ImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Image
        fields = '__all__'


class ArtistSerializer(serializers.ModelSerializer):

    class Meta:
        model = Artist
        fields = [
            'artist_id',
            'artist_uri',
            'name',
            'platform',
            'images',
        ]


class AlbumContributorSerializer(serializers.ModelSerializer):
    artist_id = serializers.CharField(source='artist.id', required=False)
    artist_uri = serializers.CharField(source='artist.uri', required=False)
    artist_name = serializers.CharField(source='artist.name', required=False)
    artist_images = serializers.CharField(source='artist.images', required=False)

    class Meta:
        model = AlbumContributor
        fields = [
            'artist_id',
            'artist_uri',
            'artist_name',
            'artist_images',
            'contribution_type',
        ]


class AlbumSerializer(serializers.ModelSerializer):
    artist = ArtistSerializer(source='album_uploaded_by', many=False, required=False)
    contributors = AlbumContributorSerializer(many=True)

    album_id = serializers.CharField(source='id', required=False)
    album_uri = serializers.CharField(source='uri', required=False)

    class Meta:
        model = Album
        fields = [
            'album_id',
            'album_uri',
            'name',
            'type',
            'platform',

            'images',

            'artist',
            'contributors',
        ]


class SongContributorSerializer(serializers.ModelSerializer):
    artist_id = serializers.CharField(source='artist.id', required=False)
    artist_uri = serializers.CharField(source='artist.uri', required=False)
    artist_name = serializers.CharField(source='artist.name', required=False)
    artist_images = ImageSerializer(source='artist.images', required=False, many=True)

    class Meta:
        model = SongContributor
        fields = [
            'artist_id',
            'artist_uri',
            'artist_name',
            'artist_images',
            'contribution_type',
        ]


class SongSerializer(serializers.ModelSerializer):
    artist = ArtistSerializer(source='song_uploaded_by', required=False, many=False)
    album = AlbumSerializer(required=False, many=False)
    contributions = SongContributorSerializer(many=True)

    song_id = serializers.CharField(source='id')
    song_uri = serializers.CharField(source='uri')

    class Meta:
        model = Song
        fields = [
            'song_id',
            'song_uri',
            'title',
            'duration',
            'genre',
            'platform',
            'is_explicit',

            'album',
            'artist',
            'contributions',
        ]
