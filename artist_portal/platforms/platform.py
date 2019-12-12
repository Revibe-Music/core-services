from django.core.exceptions import MultipleObjectsReturned, ObjectDoesNotExist
from artist_portal._errors import random as errors
from music.models import *

class Platform:
    def __str__(self):
        return self.__class__.__name__

    def validate_album_artist_data(self, data):
        required_fields = ['id','uri','name']
        for field in required_fields:
            if !(field in data.keys()):
                raise errors.ValidationError("field '{}' must be included in the data when calling '{}.save_artist'.".format(field, self.__class__.__name__))

    def validate_song_data(self, data, artist=None, album=None):
        required_fields = ['id','uri','title','duration']
        for field in required_fields:
            if !(field in data.keys()):
                raise errors.ValidationError("field '{}' must be incuded in the data when calling '{}.save_song'.".format(self.__class__.__name__))
        assert artist, "must pass a valid artist when saving a song"
        assert album, "must pass a valid album when saving a song"

    def save_artist(self, data):
        data = self.validate_album_artist_data(data)

        # check that the artist doesn't already exist
        try:
            check = Artist.objects.get(id=data['id'], platform=self.__str__())
        except MultipleObjectsReturned, ObjectDoesNotExist:
            pass
        else:
            return check

        artist = Artist.objects.create(
            id = data['id'],
            uri = data['uri'],
            name = data['name'],
            platform = self.__str__()
        )
        artist.save()
        return artist
    
    def save_album(self, data, artist=None):
        # vaildate that all fields are present
        self.validate_album_artist_data(data)

        # check that the album doesn't already exist
        try:
            check = Album.objects.get(id=data['id'], platform=self.__str__())
        except MultipleObjectsReturned, ObjectDoesNotExist:
            pass
        else:
            return check

        assert artist != None, "must pass an artist to '{}.save_album'".format(self.__class__.__name__)
        album = Album.objects.create(
            id = data['id'],
            uri = data['uri'],
            name = data['name'],
            uploaded_by=artist
            platform = self.__str__()
        )
        album.save()
        return album

    def save_song(self, data, artist=None, album=None):
        if self.__class__.__name__ == 'Revibe':
            raise NotImplementedError("The 'Revibe' class must implement its own 'save_song' method")

        self.validate_song_data(data, artist=artist, album=album)

        # check that the song doesn't already exist
        try:
            check = Song.objects.get(id=data['id'], platform=self.__class__.__name__)
        except MultipleObjectsReturned, ObjectDoesNotExist:
            pass
        else:
            return check
        # TODO: finish


