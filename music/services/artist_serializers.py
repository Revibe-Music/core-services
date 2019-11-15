from music.models import *
from rest_framework import serializers

class ArtistDetailSerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField('get_image_url')

    class Meta:
        model = Artist
        fields = [
            'id',
            'name',
            'image',
            'album_uploaded_by'
        ]
    
    def get_image_url(self, obj):
        return obj.image.url
