from django.db import models

# Create your models here.
class CustomUser(models.Model):
    # stuff here
    """
    username
    password
    """

class Profile(models.Model):

    first_name = models.CharField('First Name', max_length=255)
    last_name = models.CharField('First Name', max_length=255)
    email = models.EmailField('Email')
    profile_picture = models.ImageField("Profile Picture", upload_to='images/profiles')
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, null=False)

class Artist(models.Model):

    artist_id = models.AutoField(primary_key=True)
    artist_name = models.CharField('Display Name', max_length=255)
    artist_image = models.ImageField('Display Image', upload_to='images/artists')
    platform = models.CharField(max_length=255)
    user = models.OneToOneField(CustomUser, on_delete=models.SET_NULL, null=True, blank=True) # only has something if it's a revibe artist

class Album(models.Model):

    album_id = models.AutoField(primary_key=True)
    album_name = models.CharField(max_length=255)
    album_image = models.ImageField('Album Image', upload_to='image/albums')
    contributors = models.ManyToManyField(Artist, though='AlbumContributors')

class AlbumContributors(models.Model):

    album_id = models.ForeignKey(Album, on_delete=models.CASCADE)
    artist_id = models.ForeignKey(Artist, on_delete=models.CASCADE)
    contribution_type = models.CharField(max_length=255) # limit choices on the application side

class Song(models.Model):

    song_id = models.AutoField(primary_key=True)
    song_file = models.FileField('Song', upload_to='audio/songs')
    song_title = models.CharField('Title', max_length=255)
    duration = models.DurationField('Duration') # TODO: Check how this actually works, never used it before
    url = models.URL('URL') # TODO: Check how this field works, and if it will work with how we pull in service songs
    # stream = ???
    platform = models.CharField(max_length=255)
    uploaded_by = models.ForeignKey(Artist, on_delete=models.SET_NULL, null=True) # artist or user???
    uploaded_date = models.DateField()
    contributors = models.ManyToManyField(Artist, through='SongContributors')

class SongContributors(models.Model):

    song_id = models.ForeignKey(Song, on_delete=models.CASCADE)
    artist_id = models.ForeignKey(Artist, on_delete=models.SET_NULL)
    contribution_type = models.CharField(max_length=255) # limit choices on the application side

class Library(models.Model):

    song_id = models.ForeignKey(Song, on_delete=models.CASCADE)
    user_id = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    platform = models.CharField(max_length=255)

class Playlist(models.Model):

    song_id = models.ForeignKey(Song, on_delete=models.SET_NULL)
    user_id = models.ForeignKey(CustomUser, on_delete=models.SET_NULL)

class Social(models.Model):

    user_id = models.ForeignKey(User, on_delete=models.SET_NULL)
    paltform = models.CharField(max_length=255)
