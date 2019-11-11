from .models import *
from rest_framework import serializers


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
    artists = ArtistSerializer(many=True)
    class Meta:
        model = SongContributor
        fields = '__all__'

class SongSerializer(serializers.ModelSerializer):
    album = AlbumSerializer(many=False)
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
