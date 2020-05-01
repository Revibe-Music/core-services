"""
Created: 01 May 2020
Author: Jordan Prechac
"""

from rest_framework import serializers

from content.models import Song
from content.serializers.base import BaseSongSerializer

# -----------------------------------------------------------------------------

class DashboardSongSerializer(BaseSongSerializer):

    value = serializers.SerializerMethodField(method_name='_get_value', read_only=True)

    class Meta:
        model = Song
        fields = [
            'id',
            'uri',
            'title',
            'value',
        ]
    
    def _get_value(self, obj):
        return getattr(obj, 'value', None)
