from django.db import models
from django.conf import settings
import uuid

import music.model_exts as ext

class Artist(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField('Display Name', max_length=255)
    image = models.FileField('Display Image', upload_to='images/artists') # actual field
    platform = models.CharField(max_length=255)
    # manager = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, related_name='artist_manager', null=True, blank=True)

    def __str__(self):
        return "{}".format(self.name)
    
    def __repr__(self):
        return "<Artist: {} {}>".format(self.name, self.id)

class Album(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255, null=False)
    image = models.FileField('Album Image', upload_to='images/albums', null=True) # actual field
    # TODO: create mutliple image fields to send different sized images for different uses
    platform = models.CharField(max_length=255)
    type = models.CharField(max_length=255, null=True, blank=True)
    uploaded_by = models.ForeignKey(Artist, on_delete=models.SET_NULL, null=True, related_name="album_uploaded_by")
    contributors = models.ManyToManyField(Artist, through='AlbumContributor')
    is_displayed = models.BooleanField(null=False, blank=True, default=True)
    is_deleted = models.BooleanField(null=False, blank=True, default=False)

    def __str__(self):
        return "{}".format(self.name)
    
    def __repr__(self):
        return "<Album: {} {}>".format(self.name, self.id)

class AlbumContributor(models.Model):
    artist = models.ForeignKey(Artist, on_delete=models.CASCADE, null=False, related_name='artist_to_album')
    album = models.ForeignKey(Album, on_delete=models.CASCADE, null=False, related_name='album_to_artist')
    contribution_type = models.CharField(max_length=255, null=True) # limit choices on the application side

    def __str__(self):
        return "'{}' with '{}' as {}".format(self.album, self.artist, self.contribution_type)

    def __repr__(self):
        return "<AlbumContribution: {}-{}>".format(self.album, self.artist)

class Song(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    uri = models.UUIDField('URI', default=uuid.uuid4, unique=True, editable=False)
    file = models.FileField('Song', upload_to=ext.rename_song, null=True)
    title = models.CharField('Name', max_length=255, null=False)
    album  = models.ForeignKey(Album, on_delete=models.CASCADE, null=False, blank=False)
    duration = models.DecimalField('Duration', null=True, blank=True, max_digits=6, decimal_places=2) # seconds
    platform = models.CharField(max_length=255, null=True)
    contributors = models.ManyToManyField(Artist, through='SongContributor', related_name="song_contributors")
    uploaded_by = models.ForeignKey(Artist, on_delete=models.SET_NULL, null=True, related_name="song_uploaded_by") # artist or user???
    uploaded_date = models.DateField(auto_now_add=True, null=True, blank=True, editable=False)
    genre = models.CharField(max_length=255, null=True, blank=True)
    is_displayed = models.BooleanField(null=False, blank=True, default=True)
    is_deleted = models.BooleanField(null=False, blank=True, default=False)

    def __str__(self):
        return "{}".format(self.title)
    
    def __repr__(self):
        return "<Song: {} {}>".format(self.title, self.id)

class SongAnalysis(models.Model):
    pass

class SongContributor(models.Model):
    artist = models.ForeignKey(Artist, on_delete=models.CASCADE, null=False, related_name='artist_to_song')
    song = models.ForeignKey(Song, on_delete=models.CASCADE, null=False, related_name='song_to_artist')
    contribution_type = models.CharField(max_length=255, null=True) # limit choices on the application side

    def __str__(self):
        return "'{}' with '{}' as {}".format(self.song, self.artist, self.contribution_type)

    def __repr__(self):
        return "<SongContribution: {}-{}>".format(self.song, self.artist)

class Library(models.Model):
    platform = models.CharField(max_length=255, null=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=False)
    songs = models.ManyToManyField(Song, through='LibrarySongs', related_name='library_songs')
    
    def __str__(self):
        return "{} on {}".format(self.user, self.platform)
    
    def __repr__(self):
        return "<Library: {}-{}>".format(self.user, self.platform)

class Playlist(models.Model):
    name = models.CharField("Name", null=True, blank=False, max_length=255)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    songs = models.ManyToManyField(Song, through='PlaylistSongs', related_name='playlist_songs')

    def __str__(self):
        return "{}".format(self.name)
    
    def __repr__(self):
        return "<Playlist: {}>".format(self.name)

class LibrarySongs(models.Model):
    library = models.ForeignKey(Library, on_delete=models.CASCADE, null=False, related_name='library_to_song')
    song = models.ForeignKey(Song, on_delete=models.CASCADE, null=False, related_name='song_to_library')
    date_saved = models.DateTimeField(auto_now_add=True) # test that serializer will auto add the datetime

    def __str__(self):
        return "{} in {}".format(self.song, self.library)
    
    def __repr__(self):
        return "<LibrarySongs: {}-{}>".format(self.song, self.library)

class PlaylistSongs(models.Model):
    playlist = models.ForeignKey(Playlist, on_delete=models.CASCADE, related_name='playlist_to_song')
    song = models.ForeignKey(Song, on_delete=models.CASCADE, related_name='song_to_playlist')
    date_saved = models.DateTimeField(auto_now_add=True) # test that serializer will auto add the datetime

    def __str__(self):
        return "{} in {}".format(self.song, self.playlist)
    
    def __repr__(self):
        return "<LibrarySongs: {}-{}>".format(self.song, self.playlist)
