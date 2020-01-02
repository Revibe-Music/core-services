from revibe.platforms.base_platform import Platform
from revibe._helpers.versions import Version

from content.models import *
from content.serializers import v1 as content_ser_v1
from music.serializers import v1 as ser_v1

class Revibe(Platform):
    strings = [
        'revibe',
        'REVIBE',
        'Revibe',
        'ReVibe',
        'reVibe',
    ]

    def save_song_to_library(self, data, *args, **kwargs):
        version = kwargs.pop('version', Version().latest)

        if version == 'v1':
            serializer = ser_v1.BaseLibrarySongSerializer(data=data, *args, **kwargs)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return serializer
    
    def destroy(self, instance):
        if isinstance(instance, (Song, Album)):
            instance.is_deleted = True
            instance.save()
        else:
            instance.delete()


class YouTube(Platform):
    strings = [
        'youtube',
        'YOUTUBE',
        'Youtube',
        'YouTube',
        'youTube',
        'you tube',
        'YOU TUBE',
        'You Tube',
        'You tube',
        'you Tube',
    ]
    
    def save_album(self, data, artist, *args, **kwargs):
        serializer, album = super().save_album(data, artist=artist)
        assert album, "Error saving album"
        album.type = 'Single'
        album.save()
        return serializer, album


class Spotify(Platform):
    strings = [
        'Spotify',
        'SPOTIFY',
        'spotify',
    ]
