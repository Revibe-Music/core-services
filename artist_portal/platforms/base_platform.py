from django.core.exceptions import MultipleObjectsReturned, ObjectDoesNotExist
from artist_portal._errors import random as errors, platforms as plt_er
from artist_portal._helpers.versions import Version
from content.models import *
from music.models import *
from music.serializers import v1 as ser_v1

class Platform:

    def __init__(self, *args, **kwargs):
        if self.__class__.__name__ == 'Platform':
            raise plt_er.InvalidPlatformOperation("Cannot instantiate class 'Platform', can only create instances of a subclass")
        self.get_queries()

    def __str__(self):
        return self.__class__.__name__
    
    def __repr__(self):
        return "<class {}>".format(self.__class__.__name__)

    def get_queries(self):
        p = self.__str__()
        self.Artists = Artist.objects.filter(platform=p)
        self.Albums = Album.objects.filter(platform=p)
        self.Songs = Song.objects.filter(platform=p)
        self.AlbumContributors = AlbumContributor.objects.filter(album__platform=p)
        self.SongContributors = SongContributor.objects.filter(song__platform=p)
        if self.__str__() == 'Revibe':
            self.HiddenAlbums = Album.all_objects.filter(platform=p)
            self.HiddenSongs = Song.all_objects.filter(platform=p)

    def invalidate_revibe(self):
        if self.__class__.__name__ == 'Revibe':
            raise NotImplementedError("Class 'Revibe' must overwrite this method")

    def validate_album_artist_data(self, data):
        required_fields = ['id','uri','name']
        for field in required_fields:
            if not (field in data.keys()):
                raise errors.ValidationError("field '{}' must be included in the data when calling '{}.save_artist'.".format(field, self.__class__.__name__))

    def validate_song_data(self, data, artist=None, album=None):
        required_fields = ['song_id','uri','title','duration']
        for field in required_fields:
            if not (field in data.keys()):
                raise errors.ValidationError("field '{}' must be incuded in the data when calling '{}.save_song'.".format(self.__class__.__name__))
        assert artist, "must pass a valid artist when saving a song"
        assert album, "must pass a valid album when saving a song"
    
    def check_if_exists(self, id, obj):
        try:
            check = obj.objects.get(id=id, platform=self.__class__.__name__)
        except (MultipleObjectsReturned, ObjectDoesNotExist) as e:
            return False
        else:
            return check

    def save_artist(self, data):
        self.invalidate_revibe()
        self.validate_album_artist_data(data)

        # check that the artist doesn't already exist
        check = self.check_if_exists(data['id'], Artist)
        if check:
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
        self.invalidate_revibe()
        self.validate_album_artist_data(data)

        # check that the album doesn't already exist
        check = self.check_if_exists(data['id'], Album)
        if check:
            return check

        assert artist != None, "must pass an artist to '{}.save_album'".format(self.__class__.__name__)
        album = Album.objects.create(
            id = data['id'],
            uri = data['uri'],
            name = data['name'],
            uploaded_by=artist,
            platform = self.__str__()
        )
        album.save()

        al_contrib = AlbumContributor.objects.create(album=album, artist=artist, contribution_type="Artist")
        return album

    def save_song(self, data, artist=None, album=None):
        self.invalidate_revibe()
        self.validate_song_data(data, artist=artist, album=album)

        # check that the song doesn't already exist
        check = self.check_if_exists(data['song_id'], Song)
        if check:
            return check

        assert artist != None, "must pass an artist to '{}.save_song'".format(self.__class__.__name__)
        assert album != None, "must pass an album to '{}.save_song'".format(self.__class__.__name__)

        song = Song.objects.create(
            id=data['song_id'],
            uri=data['uri'],
            title=data['title'],
            duration=data['duration'],
            album=album,
            uploaded_by=artist,
            platform=self.__class__.__name__
        )
        song.save()

        song_contrib = SongContributor.objects.create(song=song, artist=artist, contribution_type="Artist")
        song_contrib.save()
        return song

    def save_song_to_library(self, data, *args, **kwargs):
        artist = self.save_artist(data['artist'])
        album = self.save_album(data['album'], artist=artist)
        song = self.save_song(data, artist=artist, album=album)

        version = kwargs.pop('version', Version().latest)

        if version == 'v1':
            serializer = ser_v1.BaseLibrarySongSerializer(data={'song_id': song.id}, *args, **kwargs)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return serializer
    
    def destroy(self, instance):
        self.invalidate_revibe()
        instance.delete()
        
