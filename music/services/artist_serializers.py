from music.models import *
from music.serializers import SongSerializer
from rest_framework import serializers

class ArtistAlbumSerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField('get_image_url')
    class Meta:
        model = Album
        fields = [
            'id',
            'name',
            'image',
            'platform'
        ]
    def get_image_url(self, obj):
        return obj.image.url

class ArtistSongSerializer(SongSerializer):
    """
    TODO: this
    """
    pass


class ArtistSongContributorSerializer(serializers.ModelSerializer):
    song = ArtistSongSerializer(many=False)
    
    class Meta:
        model = SongContributor
        fields = [
            'contribution_type',
            'song'
        ]
