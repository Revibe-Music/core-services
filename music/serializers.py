from .models import *
from rest_framework import serializers
from .services import song_serializers as ss


class ArtistSerializer(serializers.ModelSerializer):
    class Meta:
        model = Artist
        fields = '__all__'

class AlbumContributorSerializer(serializers.ModelSerializer):
    artist = ArtistSerializer(many=False)
    class Meta:
        model = AlbumContributor
        fields = '__all__'

class AlbumSerializer(serializers.ModelSerializer):
    contributors = AlbumContributorSerializer(many=True)
    class Meta:
        model = Album
        fields = '__all__'

class SongContributorSerializer(serializers.ModelSerializer):
    # https://www.reddit.com/r/django/comments/6yrh9k/drf_serialization_not_working_on_many_to_many/
    artist = ArtistSerializer(many=False)
    # id = serializers.ReadOnlyField(source='artist.id')
    # name = serializers.ReadOnlyField(source='artist.name')
    class Meta:
        model = SongContributor
        fields = [
            # 'id',
            # 'name',
            'artist',
            'contribution_type'
        ]

class SongSerializer(serializers.ModelSerializer):
    album = ss.SongAlbumSerializer(many=False)
    contributors = SongContributorSerializer(many=True)
    class Meta:
        model = Song
        fields = [
            'id',
            'uri',
            'title',
            'album',
            'duration',
            'platform',
            'uploaded_by',
            'uploaded_date',
            'contributors'
        ]
        extra_kwargs = {
            'uri': {'read_only': True},
            'uploaded_by': {'read_only': True},
            'uploaded_date': {'read_only': True}
        }

class LibrarySerializer(serializers.ModelSerializer):
    class Meta:
        model = Library
        fields = '__all__'

class PlaylistSerializer(serializers.ModelSerializer):
    class Meta:
        model = Playlist
        fields = '__all__'
