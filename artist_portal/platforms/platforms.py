from artist_portal.platforms.base_platform import Platform
from artist_portal._helpers.versions import Version
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
    
    def save_album(self, data, artist=None):
        album = super().save_album(data, artist=artist)
        album.type = 'Single'
        album.save()
        return album
