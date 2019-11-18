from music.models import Album, AlbumContributor
from music.serializers import SongSerializer
from rest_framework import serializers

class AlbumContributorSerializer(serializers.ModelSerializer):
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
    
    def get_image_url(self, obj):
        return obj.artist.image.url

class AlbumSongSerializer(SongSerializer):
    pass