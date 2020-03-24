"""
Created: 24 Mar. 2020
Author: Jordan Prechac
"""

from rest_framework import serializers

from content.models import Artist
from content.serializers import BaseArtistSerializer
from cloud_storage.models import File, FileShare

# -----------------------------------------------------------------------------

class FileSerializer(serializers.ModelSerializer):

    display_name = serializers.CharField(required=False)
    file_type = serializers.CharField(required=False)

    # read-only
    shared_with = BaseArtistSerializer(many=True, read_only=True)

    # write-only
    share_with = serializers.ListField(write_only=True, required=False)

    class Meta:
        model = File
        fields = [
            'id',
            'file',
            'display_name',
            'file_type',
            'shared_with',
            'share_with',
        ]

    def create(self, validated_data, *args, **kwargs):
        shared = validated_data.pop('share_with', [])

        validated_data['owner'] = self.context.get('request').user.artist
        f = super().create(validated_data, *args, **kwargs)

        for artist_id in shared:
            f.shared_with.add(Artist.objects.get(id=artist_id))
        f.save()

        return f

    def update(self, instance, validated_data, *args, **kwargs):
        shared = validated_data.pop('share_with', [])

        f = super().update(instance, validated_data, *args, **kwargs)

        for artist_id in shared:
            f.shared_with.add(Artist.objects.get(id=artist_id))
        f.save()

        return f


class FileShareSerializer(serializers.ModelSerializer):

    class Meta:
        model = FileShare
        fields = [
            'id',
            'file',
            'artist',
        ]

