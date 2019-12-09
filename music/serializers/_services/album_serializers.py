from music.mixins import ArtistImageURLMixin
from music.models import Album, AlbumContributor
from rest_framework import serializers

class AlbumContributorSerializer(serializers.ModelSerializer,ArtistImageURLMixin):
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
