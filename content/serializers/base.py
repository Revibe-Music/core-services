"""
Created: 24 Mar. 2020
Author: Jordan Prechac
"""

from rest_framework import serializers

from content.models import Album, Artist, Song

# -----------------------------------------------------------------------------


class BaseArtistSerializer(serializers.ModelSerializer):

    class Meta:
        model = Artist
        fields = [
            'id',
            'uri',
            'name',
            'platform',
        ]
    
    def create(self, validated_data, *args, **kwargs):
        pass
    def update(self, validated_data, *args, **kwargs):
        pass


class BaseSongSerializer(serializers.ModelSerializer):

    class Meta:
        model = Song
        fields = [
            'id',
            'uri',
            'title',
            'duration',
            'genre',
            'platform',
            'is_explicit',
            'is_displayed',
        ]
    
    def create(self, validated_data, *args, **kwargs):
        pass
    def update(self, validated_data, *args, **kwargs):
        pass


