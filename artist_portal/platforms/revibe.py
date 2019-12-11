from artist_portal._errors.versions import VersionError
from music.serializers import v1 as ser_v1

class Revibe:
    strings = [
        'revibe',
        'REVIBE',
        'Revibe',
        'ReVibe',
        'reVibe',
    ]

    def __str__(self):
        return "Revibe"

    @classmethod
    def save_to_library(cls, data, version=None, *args, **kwargs):
        assert version != None, "function 'Revibe.save_to_library()' must contain a version number"
        if version == 'v1':
            serializer = ser_v1.BaseLibrarySongSerializer(data=data, *args, **kwargs)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return serializer

