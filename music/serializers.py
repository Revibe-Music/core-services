from .models import *
from rest_framework import serializers


class ArtistSerializer(serializers.ModelSerializer):
    class Meta:
        model = Artist
        fields = ['id', 'name', 'image', 'platform']

class AlbumContributorSerializer(serializers.ModelSerializer):
    artist = ArtistSerializer(many=False)
    class Meta:
        model = AlbumContributors
        fields = ['artist', 'contribution_type']

class AlbumSerializer(serializers.ModelSerializer):
    contributors = AlbumContributorSerializer(many=True)
    class Meta:
        model = Album
        fields = ['id', 'name', 'image', 'contributors']

class SongContributorSerializer(serializers.ModelSerializer):
    artist = ArtistSerializer(many=False)
    class Meta:
        model = SongContributors
        fields = ['artist', 'contribution_type']

class SongSerializer(serializers.ModelSerializer):
    album = AlbumSerializer(many=False)
    contributors = SongContributorSerializer(many=True)
    class Meta:
        model = Song
        fields = ['id', 'uri', 'name', 'album', 'duration', 'platform', 'contributors']

class LibrarySerializer(serializers.ModelSerializer):
    class Meta:
        model = Library
        fields = '__all__'

class PlaylistSerializer(serializers.ModelSerializer):
    class Meta:
        model = Playlist
        fields = '__all__'
