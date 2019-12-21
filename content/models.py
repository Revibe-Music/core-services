from django.db import models
from django.utils.timezone import now
import uuid

from content import model_exts as ext
from content.managers import *


# class Image(models.Model):
#     file = models.FileField(null=True, blank=True, default=None)
#     reference = models.CharField(max_length=255, null=True, blank=True, default=None)

#     height = models.IntegerField(null=False, blank=False)
#     width = models.IntegerField(null=False, blank=False)

#     def __str__(self):
#         if self.reference != None:
#             return self.reference
#         else:
#             return "{} ({}x{})".format(self.file.name, self.height, self.width)
    
#     class Meta:
#         verbose_name = 'image'
#         verbose_name_plural = 'images'


class Artist(models.Model):
    id = models.CharField(max_length=255, primary_key=True, default=uuid.uuid4, editable=False)
    uri = models.CharField(max_length=255, default=uuid.uuid4, unique=True, editable=False)
    name = models.CharField(max_length=255, null=False, blank=False)
    image = models.FileField(upload_to=ext.rename_image, null=True, blank=True)
    platform = models.CharField(max_length=255, null=False, blank=False)

    objects = models.Manager()

    def __str__(self):
        return "{}".format(self.name)
    
    def __repr__(self):
        return "<Artist: {} {}>".format(self.name, self.id)
    
    class Meta:
        verbose_name = 'artist'
        verbose_name_plural = 'artists'


class Album(models.Model):
    id = models.CharField(max_length=255, primary_key=True, default=uuid.uuid4, editable=False)
    uri = models.CharField(max_length=255, unique=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255, null=False)
    type = models.CharField(max_length=255, null=True, blank=True)
    image = models.FileField(upload_to=ext.rename_image, null=True, blank=True)
    platform = models.CharField(max_length=255, null=False, blank=False)

    date_added = models.DateTimeField(auto_now_add=True, null=True, editable=False)
    last_changed = models.DateTimeField(auto_now=True, null=True)
    date_published = models.DateField(null=True, blank=True, default=now)
    is_displayed = models.BooleanField(null=False, blank=True, default=True)
    is_deleted = models.BooleanField(null=False, blank=True, default=False)

    objects = models.Manager()
    uploaded_by = models.ForeignKey(Artist, on_delete=models.SET_NULL, null=True, related_name="album_uploaded_by")
    contributors = models.ManyToManyField(Artist, through='AlbumContributor')

    def __str__(self):
        return "{}".format(self.name)
    
    def __repr__(self):
        return "<Album: {} {}>".format(self.name, self.id)

    objects = models.Manager()
    hidden_objects = NotDeletedManager()
    display_objects = NotHiddenNotDeletedManager()

    class Meta:
        verbose_name = 'album'
        verbose_name_plural = 'albums'


class AlbumContributor(models.Model):
    artist = models.ForeignKey(Artist, on_delete=models.CASCADE, null=False, related_name='artist_to_album')
    album = models.ForeignKey(Album, on_delete=models.CASCADE, null=False, related_name='album_to_artist')
    contribution_type = models.CharField(max_length=255, null=True)
    pending = models.BooleanField(null=False, blank=True, default=False)
    approved = models.BooleanField(null=False, blank=True, default=True)

    date_added = models.DateField(auto_now_add=True, null=True, editable=False)
    last_changed = models.DateField(auto_now=True, null=True)
    primary_artist = models.BooleanField(null=False, blank=True, default=False)

    objects = models.Manager()
    hidden_objects = HiddenAlbumContributorManager()
    display_objects = AlbumContributorDisplayManager()

    def __str__(self):
        return "'{}' with '{}' as {}".format(self.album, self.artist, self.contribution_type)

    def __repr__(self):
        return "<AlbumContribution: {}-{}>".format(self.album, self.artist)
    
    class Meta:
        verbose_name = 'album contributor'
        verbose_name_plural = 'album contributors'


class Song(models.Model):
    id = models.CharField(primary_key=True, default=uuid.uuid4, editable=False, max_length=255)
    uri = models.CharField('URI', default=uuid.uuid4, unique=True, editable=False, max_length=255)
    file = models.FileField('Song', upload_to=ext.rename_song, null=True, blank=True)
    title = models.CharField('Name', max_length=255, null=False)
    duration = models.DecimalField('Duration', null=True, blank=True, max_digits=6, decimal_places=2) # in seconds
    genre = models.CharField(max_length=255, null=True, blank=True)
    platform = models.CharField(max_length=255, null=True)
    is_explicit = models.BooleanField(null=False, blank=True, default=False)

    is_displayed = models.BooleanField(null=False, blank=True, default=True)
    is_deleted = models.BooleanField(null=False, blank=True, default=False)
    last_changed = models.DateField(auto_now=True, null=True, blank=True)
    uploaded_date = models.DateField(auto_now_add=True, null=True, blank=True, editable=False)

    album  = models.ForeignKey(Album, on_delete=models.CASCADE, null=False, blank=False)
    contributors = models.ManyToManyField(Artist, through='SongContributor', related_name="song_contributors")
    uploaded_by = models.ForeignKey(Artist, on_delete=models.SET_NULL, null=True, related_name="song_uploaded_by") # artist or user???

    objects = models.Manager() # all objects
    hidden_objects = NotDeletedManager() # objects that are not deleted
    display_objects = NotHiddenNotDeletedManager() # objects that are not deleted and not hidden

    def __str__(self):
        return "{}".format(self.title)
    
    def __repr__(self):
        return "<Song: {} {}>".format(self.title, self.id)
    
    class Meta:
        verbose_name = 'song'
        verbose_name_plural = 'songs'


class SongContributor(models.Model):
    artist = models.ForeignKey(Artist, on_delete=models.CASCADE, null=False, related_name='artist_to_song')
    song = models.ForeignKey(Song, on_delete=models.CASCADE, null=False, related_name='song_to_artist')
    contribution_type = models.CharField(max_length=255, null=True)
    pending = models.BooleanField(null=False, blank=True, default=False)
    approved = models.BooleanField(null=False, blank=True, default=True)

    date_added = models.DateField(auto_now_add=True, null=True, editable=False)
    last_changed = models.DateField(auto_now=True, null=True)
    primary_artist = models.BooleanField(null=False, blank=True, default=False)

    objects = models.Manager()
    hidden_objects = HiddenSongContributorManager()
    display_objects = SongContributorDisplayManager()

    def __str__(self):
        return "'{}' with '{}' as {}".format(self.song, self.artist, self.contribution_type)

    def __repr__(self):
        return "<SongContribution: {}-{}>".format(self.song, self.artist)
    
    class Meta:
        verbose_name = 'song contributor'
        verbose_name_plural = 'song contributors'

