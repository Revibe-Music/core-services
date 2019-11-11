from music.models import *
from rest_framework import serializers

class SongAlbumSerializer(serializers.ModelSerializer):
    class Meta:
        model = Album
        fields = [
            'id',
            'name'
        ]

class SongContributionSerializer(serializers.RelatedField):
    def to_representation(self, value):
        out = {
            'id': value.id,
            'name': value.name
        }
        return out