"""
Created: 01 May 2020
Author: Jordan Prechac
"""

from rest_framework import serializers

from content.models import Song
from content.serializers.base import BaseSongSerializer

# -----------------------------------------------------------------------------

class DashboardSongSerializer(BaseSongSerializer):

    def __init__(self, *args, **kwargs):
        super(DashboardSongSerializer, self).__init__(*args, **kwargs)

        extra_fields = self.context.get('extra_fields', None)
        if extra_fields is not None:
            for field_name in extra_fields:
                # TODO: Build in security check to make sure user's can't access improper data, like passwords n shit
                # security check
                if 'password' in field_name:
                    continue

                # create method for getting the additional field
                exec(f"""DashboardSongSerializer.get_{field_name} = lambda self, obj : getattr(obj, '{field_name}', None)""")
                self.fields[field_name] = serializers.SerializerMethodField(read_only=True)


    class Meta:
        model = Song
        fields = [
            'id',
            'uri',
            'title',
        ]
    
