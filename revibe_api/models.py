from django.db import models
from django.conf import settings
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db.models.signals import post_save
from django.dispatch import receiver

# Create your models here.

class Artist(models.Model):

    id = models.AutoField(primary_key=True)
    name = models.CharField('Display Name', max_length=255)
    image = models.FileField('Display Image', upload_to='images/artists')
    platform = models.CharField(max_length=255)
    manager = models.ForeignKey('CustomUser', on_delete=models.SET_NULL, related_name='artist_manager', null=True)

class CustomUser(AbstractUser):
    
    artist = models.OneToOneField(Artist, on_delete=models.SET_NULL, related_name='artist_user', null=True, blank=True)


class Profile(models.Model):

    id = models.AutoField(primary_key=True)
    country = models.CharField('Country', max_length=255, null=True)
    # replace with???
    # lat = models.???
    # long = models.???
    dob = models.DateField('Date of Birth', null=True)
    image = models.FileField("Profile Picture", upload_to='images/profiles', null=True)
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=False)


# creates what are basically event listeners to create and save a profile whenever a user is created
@receiver(post_save, sender=CustomUser)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)

@receiver(post_save, sender=CustomUser)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()

class Album(models.Model):

    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255, null=False)
    image = models.FileField('Album Image', upload_to='image/albums', null=True)
    contributors = models.ManyToManyField(Artist, through='AlbumContributors')

class AlbumContributors(models.Model):

    album = models.ForeignKey(Album, on_delete=models.CASCADE, null=False)
    artist = models.ForeignKey(Artist, on_delete=models.CASCADE, null=False)
    contribution_type = models.CharField(max_length=255, null=True) # limit choices on the application side

class Song(models.Model):

    id = models.AutoField(primary_key=True)
    file = models.FileField('Song', upload_to='audio/songs', null=False)
    title = models.CharField('Title', max_length=255, null=False)
    duration = models.IntegerField('Duration', null=True)
    uri = models.CharField('URI', max_length=255, unique=True)
    # stream = ???
    platform = models.CharField(max_length=255, null=True)
    uploaded_by = models.ForeignKey(Artist, on_delete=models.SET_NULL, null=True, related_name="song_uploaded_by") # artist or user???
    uploaded_date = models.DateField(null=True)
    contributors = models.ManyToManyField(Artist, through='SongContributors', related_name="song_contributors")

class SongContributors(models.Model):

    song = models.ForeignKey(Song, on_delete=models.CASCADE, null=False)
    artist = models.ForeignKey(Artist, on_delete=models.CASCADE, null=False)
    contribution_type = models.CharField(max_length=255, null=True) # limit choices on the application side

class Library(models.Model):

    song = models.ForeignKey(Song, on_delete=models.CASCADE, null=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=False)
    platform = models.CharField(max_length=255, null=True)

class Playlist(models.Model):

    song = models.ForeignKey(Song, on_delete=models.SET_NULL, null=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)

class Social(models.Model):

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    paltform = models.CharField(max_length=255, null=True)
