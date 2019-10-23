from django.db import models

# Create your models here.

class Artist(models.Model):

    name = models.CharField(max_length=255, blank=False, null=False)
    image = models.FileField(upload_to='artist_images', blank=True, null=True)

    def __str__(self):
        return str(self.name)
    
    class Meta:
        verbose_name = 'Artist'
        verbose_name_plural = 'Artists'

class Album(models.Model):

    name = models.CharField(max_length=255, blank=False, null=False)
    image = models.FileField(upload_to='album_image', blank=True, null=True)
    artist = models.ForeignKey(Artist, blank=True, null=True, on_delete=models.SET_NULL)

    def __str__(self):
        return str(self.name)
    
    class Meta:
        verbose_name = 'Album'
        verbose_name_plural = 'Albums'

class Song(models.Model):

    song = models.FileField(upload_to='songs', blank=False, null=False)
    title = models.CharField(max_length=255, blank=False, null=False)
    artist = models.ForeignKey(Artist, blank=False, null=True, on_delete=models.SET_NULL)
    album = models.ForeignKey(Album, blank=False, null=True, on_delete=models.SET_NULL)
    duration = models.IntegerField(blank=False, null=False)

    def __str__(self):
        return "{} by {}".format(self.title, self.artist)
    
    class Meta:
        verbose_name = 'Song'
        verbose_name_plural = 'Songs'
