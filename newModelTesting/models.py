from django.db import models
from django.conf import settings

# Create your models here.
class CustomUser(models.Model):
    # stuff here
    """
    username
    password
    Anything else? Links to Artist and Profile are in those classes
    """

class Profile(models.Model):

    first_name = models.CharField('First Name', max_length=255)
    last_name = models.CharField('First Name', max_length=255)
    email = models.EmailField('Email')
    profile_picture = models.FileField("Profile Picture", upload_to='images/profiles')
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=False)

class Artist(models.Model):

    artist_id = models.AutoField(primary_key=True)
    artist_name = models.CharField('Display Name', max_length=255)
    artist_image = models.FileField('Display Image', upload_to='images/artists')
    platform = models.CharField(max_length=255)
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True) # only has something if it's a revibe artist

class Album(models.Model):

    album_id = models.AutoField(primary_key=True)
    album_name = models.CharField(max_length=255)
    album_image = models.FileField('Album Image', upload_to='image/albums')
    contributors = models.ManyToManyField(Artist, through='AlbumContributors')

class AlbumContributors(models.Model):

    album_id = models.ForeignKey(Album, on_delete=models.CASCADE)
    artist_id = models.ForeignKey(Artist, on_delete=models.CASCADE)
    contribution_type = models.CharField(max_length=255) # limit choices on the application side

class Song(models.Model):

    song_id = models.AutoField(primary_key=True)
    song_file = models.FileField('Song', upload_to='audio/songs')
    song_title = models.CharField('Title', max_length=255)
    duration = models.DurationField('Duration') # TODO: Check how this actually works, never used it before
    url = models.URLField('URL') # TODO: Check how this field works, and if it will work with how we pull in service songs
    # stream = ???
    platform = models.CharField(max_length=255)
    uploaded_by = models.ForeignKey(Artist, on_delete=models.SET_NULL, null=True, related_name="song_uploaded_by") # artist or user???
    uploaded_date = models.DateField()
    contributors = models.ManyToManyField(Artist, through='SongContributors', related_name="song_contributors")

class SongContributors(models.Model):

    song_id = models.ForeignKey(Song, on_delete=models.CASCADE, null=False)
    artist_id = models.ForeignKey(Artist, on_delete=models.CASCADE, null=False)
    contribution_type = models.CharField(max_length=255) # limit choices on the application side

class Library(models.Model):

    song_id = models.ForeignKey(Song, on_delete=models.CASCADE)
    user_id = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    platform = models.CharField(max_length=255)

class Playlist(models.Model):

    song_id = models.ForeignKey(Song, on_delete=models.SET_NULL, null=True)
    user_id = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)

class Social(models.Model):

    user_id = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    paltform = models.CharField(max_length=255)
