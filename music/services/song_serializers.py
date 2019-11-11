from music.models import *
from rest_framework import serializers

class SongAlbumSerializer(serializers.ModelSerializer):
    class Meta:
        model = Album
        fields = [
            'id',
            'name'
        ]

class SongContributorSerializer(serializers.ModelSerializer):
    # https://www.reddit.com/r/django/comments/6yrh9k/drf_serialization_not_working_on_many_to_many/
    id = serializers.ReadOnlyField(source='artist.id')
    name = serializers.ReadOnlyField(source='artist.name')
    class Meta:
        model = SongContributor
        fields = [
            'id',
            'name',
            'contribution_type'
        ]