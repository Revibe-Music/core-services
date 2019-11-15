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
    image = models.FileField('Album Image', upload_to='images/albums') # actual field
    # TODO: create mutliple image fields to send different sized images for different uses
    platform = models.CharField(max_length=255)
    uploaded_by = models.ForeignKey(Artist, on_delete=models.SET_NULL, null=True, related_name="album_uploaded_by")
    contributors = models.ManyToManyField(Artist, through='AlbumContributor')

    def __str__(self):
        return "{}".format(self.name)
    
    def __repr__(self):
        return "<Album: {} {}>".format(self.name, self.id)

class AlbumContributor(models.Model):
    artist = models.ForeignKey(Artist, on_delete=models.CASCADE, null=False, related_name='artist_to_album')
    album = models.ForeignKey(Album, on_delete=models.CASCADE, null=False, related_name='album_to_artist')
    contribution_type = models.CharField(max_length=255, null=True) # limit choices on the application side

    def __str__(self):
        return "'{}' with '{}' as {}".format(self.artist, self.album, self.contribution_type)

    def __repr__(self):
        return "<AlbumContribution: {}-{}>".format(self.album, self.artist)

class Song(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    uri = models.UUIDField('URI', default=uuid.uuid4, unique=True, editable=False)
    file = models.FileField('Song', upload_to=ext.rename_song, null=True)
    title = models.CharField('Name', max_length=255, null=False)
    album  = models.ForeignKey(Album, on_delete=models.SET_NULL, null=True, blank=True)
    duration = models.DecimalField('Duration', null=True, blank=True, max_digits=6, decimal_places=2) # seconds
    platform = models.CharField(max_length=255, null=True)
    contributors = models.ManyToManyField(Artist, through='SongContributor', related_name="song_contributors")
    uploaded_by = models.ForeignKey(Artist, on_delete=models.SET_NULL, null=True, related_name="song_uploaded_by") # artist or user???
    uploaded_date = models.DateField(null=True) # need to save the date when object is created
    genre = models.CharField(max_length=255, null=True, blank=True)

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
    songs = models.ManyToManyField(Song)
    
    def __str__(self):
        return "{} on {}".format(self.user, self.platform)
    
    def __repr__(self):
        return "<Library: {}-{}>".format(self.user.verbose_name, self.platform)

class Playlist(models.Model):
    name = models.CharField("Name", null=True, blank=False, max_length=255)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    songs = models.ManyToManyField(Song)

    def __str__(self):
        return "{}".format(self.name)
    
    def __repr__(self):
        return "<Playlist: {}>".format(self.name)
