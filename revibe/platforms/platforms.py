from rest_framework.serializers import ValidationError

from logging import getLogger
logger = getLogger(__name__)

from revibe.platforms.base_platform import Platform
from revibe._errors import data as data_err, versions
from revibe._helpers.versions import Version

from content.models import *
from content.serializers import v1 as content_ser_v1
from music.serializers import v1 as ser_v1

# -----------------------------------------------------------------------------

class Revibe(Platform):
    strings = [
        'revibe',
        'REVIBE',
        'Revibe',
        'ReVibe',
        'reVibe',
    ]

    def save(self, data, *args, **kwargs):
        return self.get_song(data, None, None, *args, **kwargs)
    
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

    def get_album(self, data, artist, *args, **kwargs):
        """
        Overwrites the base platform get_album because YouTube content will not
        have an album ID by default, so we need to create an arbitrary album to
        fit our DB schema.
        """
        # validate data
        if (not data['song']) or (not data['song']['song_id']):
            raise data_err.SerializerValidationError({"song": ["song object must contain an ID"]})
        if 'image_refs' not in data['album'].keys():
            raise data_err.SerializerValidationError({"album": ["album object must contain an image_refs"]})

        album_data = {
            "name": data['song']['title'],
            "image_refs": data['album']['image_refs']
        }

        return self._save_album(album_data, artist, *args, **kwargs)

    def save(self, data, *args, **kwargs):
        """
        Overwrites the base platform save because YouTube content will never
        have an album_id in the data because YouTube does not have albums.
        """
        # first make sure this song hasn't already been saved...
        try:
            song = Song.objects.get(id=data['song']['song_id'])
            return song
        except Song.DoesNotExist as dne:
            pass

        # if not, do it all...
        artist = self.get_artist(data, *args, **kwargs)
        album = self.get_album(data, artist, *args, **kwargs)
        song = self.get_song(data, artist, album, *args, **kwargs)

        return song


class Spotify(Platform):
    strings = [
        'Spotify',
        'SPOTIFY',
        'spotify',
    ]
