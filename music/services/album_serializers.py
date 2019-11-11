from music.models import Album, AlbumContributor
from rest_framework import serializers

class AlbumContributorSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField(source='artist.id')
    name = serializers.ReadOnlyField(source='artist.name')
    class Meta:
        model = AlbumContributor
        fields = [
            'id',
            'name',
            'contribution_type'
        ]
