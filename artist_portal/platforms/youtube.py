from artist_portal._errors.random import ValidationError
from artist_portal._helpers.debug import debug_print
from music.models import (
    Album, Artist,
    Song, Library, LibrarySongs
)

class YouTube:
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

    def __str__(self):
        return "YouTube"
    
    def get_library(self, user, *args, **kwargs):
        request = kwargs['context']['request']
        user = request.user
        library = Library.objects.filter(platform=self.__str__(), user=user)
        if len(library) != 1:
            raise ValidationError("Error finding user's library: found {} library(s)".format(len(library)))
        return library[0]
    
    def song_in_library(self, song_id):
        songs = Song.objects.filter(id=song_id, platform=self.__str__())
        return True if (len(songs) > 0) else False
    
    def save_album_artist(self, data):
        artist = Artist.objects.create(
            id=data['artist']['id'],
            uri=data['artist']['uri'],
            name=data['artist']['name']
        )
        artist.save()
        album = Album.objects.create(
            id=data['album']['id'],
            uri=data['album']['uri'],
            name=data['album']['name'],
            uploaded_by=artist
        )
        album.save()
        return (artist,album)

    def save_song(self, data):
        artist, album = self.save_album_artist(data)
        song = Song.objects.create(
            id=data['song_id'],
            uri=data['uri'],
            title=data['title'],
            duration=data['duration'],
            album=album,
            uploaded_by=artsit
        )
        song.save()
        return song

    def save_to_library(self, data, version=None, *args, **kwargs):
        required_fields = ['song_id','uri','title','duration','artist','album']
        for field in required_fields:
            assert field in data.keys(), "field '{}' must be included when saving a YouTube song.".format(field)

        # save the song if it doesn't exist in the library
        if not self.song_in_library(data['song_id']):
            song = self.save_song(data)
        else:
            song = Song.objects.get(id=data['song_id'])

        library = self.get_library(*args, **kwargs)
        lib_song = LibrarySongs.objects.create(library=library, song=song)
        lib_song.save()

        return lib_song
