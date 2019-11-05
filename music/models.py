from django.db import models
from django.conf import settings
import uuid

class Artist(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField('Display Name', max_length=255)
    image = models.FileField('Display Image', upload_to='images/artists')
    platform = models.CharField(max_length=255)
    manager = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, related_name='artist_manager', null=True, blank=True)

    def __str__(self):
        return "{} ({})".format(self.name, self.id)

class Album(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255, null=False)
    image = models.FileField('Album Image', upload_to='image/albums', null=True)
    contributors = models.ManyToManyField(Artist, through='AlbumContributors')

    def __str__(self):
        return "{} ({})".format(self.name, self.id)

class AlbumContributors(models.Model):
    artist = models.ForeignKey(Artist, on_delete=models.CASCADE, null=False)
    album = models.ForeignKey(Album, on_delete=models.CASCADE, null=False)
    contribution_type = models.CharField(max_length=255, null=True) # limit choices on the application side

class Song(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    uri = models.CharField('URI', max_length=255, unique=True) #, null=False, blank=True
    file = models.FileField('Song', upload_to='audio/songs', null=True)
    name = models.CharField('Name', max_length=255, null=False)
    album  = models.ForeignKey(Album, on_delete=models.SET_NULL, null=True, blank=True)
    duration = models.DecimalField('Duration', null=True, blank=True, max_digits=6, decimal_places=2) # seconds
    platform = models.CharField(max_length=255, null=True)
    contributors = models.ManyToManyField(Artist, through='SongContributors', related_name="song_contributors")
    uploaded_by = models.ForeignKey(Artist, on_delete=models.SET_NULL, null=True, related_name="song_uploaded_by") # artist or user???
    uploaded_date = models.DateField(null=True) # need to save the date when object is created

    def __str__(self):
        return "{} ({})".format(self.title, self.id)

class SongContributors(models.Model):
    artist = models.ForeignKey(Artist, on_delete=models.CASCADE, null=False)
    song = models.ForeignKey(Song, on_delete=models.CASCADE, null=False)
    contribution_type = models.CharField(max_length=255, null=True) # limit choices on the application side

class Library(models.Model):
    platform = models.CharField(max_length=255, null=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=False)
    songs = models.ManyToManyField(Song)

class Playlist(models.Model):
    name = models.CharField("Name", null=True, blank=False, max_length=255)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    songs = models.ManyToManyField(Song)
