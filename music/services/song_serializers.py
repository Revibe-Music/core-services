from music.models import *
from rest_framework import serializers

class SongAlbumSerializer(serializers.ModelSerializer):
    class Meta:
        model = Album
        fields = [
            'id',
            'name'
        ]