from .models import *
from rest_framework import serializers


class ArtistSerializer(serializers.ModelSerializer):
    class Meta:
        model = Artist
        fields = '__all__'

class AlbumContributorSerializer(serializers.ModelSerializer):
    artist = ArtistSerializer(many=False)
    class Meta:
        model = AlbumContributors
        fields = '__all__'

class AlbumSerializer(serializers.ModelSerializer):
    contributors = AlbumContributorSerializer(many=True)
    class Meta:
        model = Album
        fields = '__all__'

class SongContributorSerializer(serializers.ModelSerializer):
    artist = ArtistSerializer(many=False)
    class Meta:
        model = SongContributors
        fields = '__all__'

class SongSerializer(serializers.ModelSerializer):
    album = AlbumSerializer(many=False)
    contributors = SongContributorSerializer(many=True)
    class Meta:
        model = Song
        fields = '__all__'

class LibrarySerializer(serializers.ModelSerializer):
    class Meta:
        model = Library
        fields = '__all__'

class PlaylistSerializer(serializers.ModelSerializer):
    class Meta:
        model = Playlist
        fields = '__all__'
