from music.models import *
from music.mixins import ImageURLMixin, ArtistImageURLMixin
from rest_framework import serializers

class SongAlbumSerializer(serializers.ModelSerializer, ImageURLMixin):
    class Meta:
        model = Album
        fields = [
            'id',
            'uri',
            'name',
            'platform',
            'type',
        ]

class SongContributorSerializer(serializers.ModelSerializer,ArtistImageURLMixin):
    # https://www.reddit.com/r/django/comments/6yrh9k/drf_serialization_not_working_on_many_to_many/
    contribution_id = serializers.ReadOnlyField(source='id')
    id = serializers.ReadOnlyField(source='artist.id')
    uri = serializers.ReadOnlyField(source='artist.uri')
    name = serializers.ReadOnlyField(source='artist.name')

    class Meta:
        model = SongContributor
        fields = [
            'contribution_id',
            'id',
            'uri',
            'name',
            'contribution_type'
        ]