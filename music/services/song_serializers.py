from music.models import *
from music.mixins import ImageURLMixin, ArtistImageURLMixin
from rest_framework import serializers

class SongAlbumSerializer(serializers.ModelSerializer, ImageURLMixin):
    class Meta:
        model = Album
        fields = [
            'id',
            'name',
            'image',
            'platform',
            'type',
        ]

class SongContributorSerializer(serializers.ModelSerializer,ArtistImageURLMixin):
    # https://www.reddit.com/r/django/comments/6yrh9k/drf_serialization_not_working_on_many_to_many/
    id = serializers.ReadOnlyField(source='artist.id')
    name = serializers.ReadOnlyField(source='artist.name')
    image = serializers.SerializerMethodField('get_image_url')

    class Meta:
        model = SongContributor
        fields = [
            'id',
            'name',
            'image',
            'contribution_type'
        ]