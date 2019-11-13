from .models import *
from rest_framework import serializers
from .services import song_serializers, album_serializers


class ArtistSerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField('get_image_url')

    class Meta:
        model = Artist
        fields = '__all__'
    
    def get_image_url(self, obj):
        return obj.image.url

class SongSerializer(serializers.ModelSerializer):
    album = song_serializers.SongAlbumSerializer(many=False)
    song_to_artist = song_serializers.SongContributorSerializer(many=True)
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
            'song_to_artist'
        ]
        extra_kwargs = {
            'uri': {'read_only': True},
            'uploaded_by': {'read_only': True},
            'uploaded_date': {'read_only': True}
        }

class AlbumSerializer(serializers.ModelSerializer):
    album_to_artist = album_serializers.AlbumContributorSerializer(many=True)
    song_set = SongSerializer(many=True)
    image = serializers.SerializerMethodField('get_image_url')

    class Meta:
        model = Album
        fields = [
            'id',
            'name',
            'image',
            'uploaded_by',
            'album_to_artist',
            'song_set'
        ]
    
    def get_image_url(self, obj):
        return obj.image.url

class LibrarySerializer(serializers.ModelSerializer):
    songs = SongSerializer(many=True)
    class Meta:
        model = Library
        fields = ['platform','songs']

class PlaylistSerializer(serializers.ModelSerializer):
    class Meta:
        model = Playlist
        fields = '__all__'
