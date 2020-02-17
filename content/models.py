from django.conf import settings
from django.db import models
from django.utils.html import format_html
from django.utils.timezone import now
from django.utils.translation import gettext_lazy as _
import uuid

from content import model_exts as ext
from content.managers import *

# -----------------------------------------------------------------------------

class Image(models.Model):
    artist = models.ForeignKey(
        'content.Artist',
        on_delete=models.CASCADE,
        related_name="artist_image",
        null=True, blank=True
    )
    album = models.ForeignKey(
        'content.Album',
        on_delete=models.CASCADE,
        related_name="album_image",
        null=True, blank=True
    )

    file = models.FileField(
        help_text="The file that will be uploaded / is uploaded in S3",
        upload_to=ext.custom_image_upload,
        null=True, blank=True, default=None
    )
    reference = models.CharField(
        help_text="Reference to the file location if it is not a revibe image",
        max_length=255, null=True, blank=True, default=None
    )
    height = models.IntegerField(null=False, blank=False)
    width = models.IntegerField(null=False, blank=False)

    is_original = models.BooleanField(
        help_text="Shows if the uploaded file is the original file uploaded by the user",
        null=False, blank=True, default=True,
        verbose_name="original file status"
    )

    def __str__(self):
        return f"{self.obj.name} ({self.dimensions})"
    
    def __repr__(self):
        if self.file_path:
            return "<{}: {} ({})".format(self.__class__.__name__, self.url, self.dimensions)
        else:
            return "<{}: ({})".format(self.__class__.__name__, self.dimensions)

    @property
    def obj(self):
        if self.artist:
            return self.artist
        elif self.album:
            return self.album
        return None

    @property
    def url(self):
        if self.file:
            if settings.USE_S3:
                u = settings.MEDIA_URL
            else:
                u = "fuck it/"
            return f"{u}{self.file.name}"
        elif self.reference:
            return self.reference
        return None
    
    def _link_url(self):
        return format_html(
            "<a href={} target='_blank'>{}</a>",
            self.url,
            "Go to image"
        )
    _link_url.short_description = "url"

    @property
    def dimensions(self):
        return "{}x{}".format(self.width,self.height)

    class Meta:
        verbose_name = 'image'
        verbose_name_plural = 'images'


class Track(models.Model):
    song = models.ForeignKey(
        'content.Song',
        related_name="tracks",
        on_delete=models.CASCADE,
        null=False, blank=False
    )

    file = models.FileField(
        help_text="The audio file itself",
        upload_to=ext.custom_audio_upload,
        null=True, blank=True
    )
    reference = models.CharField(
        help_text="Reference to the song location if it is not a revibe song",
        max_length=255, null=True, blank=True
    )

    is_original = models.BooleanField(
        help_text="Shows if the uploaded file is the original file uploaded by the user",
        null=False, blank=True, default=True,
        verbose_name="original file status"
    )

    def __str__(self):
        ext = self.url.split('/')[-1]
        return f"{self.song.title} ({ext})"

    @property
    def url(self):
        if self.file:
            if settings.USE_S3:
                u = settings.MEDIA_URL
            else:
                u = "fuck it/"
            return f"{u}{self.file.name}"
        elif self.reference:
            return self.reference
        return None

    def _link_url(self):
        return format_html(
            "<a href={} target='_blank'>{}</a>",
            self.url,
            "Go to track"
        )
    _link_url.short_description = "url"

    def _audio_controls(self):
        link = self.url
        return format_html(
            f"""<audio controls>
                <source src="{link}"
                type="audio/{link.split('.')[-1]}"
                preload="none" />
            </audio>"""
        )

    class Meta:
        verbose_name = "track"
        verbose_name_plural = "tracks"


class Artist(models.Model):
    id = models.CharField(max_length=255, primary_key=True, default=uuid.uuid4, editable=False)
    uri = models.CharField(max_length=255, default=uuid.uuid4, unique=True, editable=False)
    name = models.CharField(max_length=255, null=False, blank=False)
    platform = models.CharField(max_length=255, null=False, blank=False)
    # artist_image = one-to-many with 'Image'

    date_joined = models.DateTimeField(auto_now_add=True, null=True, blank=True, editable=False)

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
    platform = models.CharField(max_length=255, null=False, blank=False)
    # album_image = one-to-many with 'Image'

    uploaded_date = models.DateField(auto_now_add=True, null=True, editable=False)
    last_changed = models.DateField(auto_now=True, null=True)
    date_published = models.DateField(null=True, blank=True, default=now)
    is_displayed = models.BooleanField(
        null=False, blank=True, default=True,
        verbose_name=_("display status")
    )
    is_deleted = models.BooleanField(
        null=False, blank=True, default=False,
        verbose_name=_("deletion status")
    )

    uploaded_by = models.ForeignKey(Artist, on_delete=models.SET_NULL, null=True, related_name="album_uploaded_by")
    contributors = models.ManyToManyField(Artist, through='AlbumContributor')
    tags = models.ManyToManyField(
        to='content.tag',
        related_name='albums',
        help_text=_("Associated tags")
    )

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
        ordering = ['name',]


class AlbumContributor(models.Model):
    artist = models.ForeignKey(Artist, on_delete=models.CASCADE, null=False, related_name='artist_to_album')
    album = models.ForeignKey(Album, on_delete=models.CASCADE, null=False, related_name='album_to_artist')
    contribution_type = models.CharField(max_length=255, null=True)
    pending = models.BooleanField(null=False, blank=True, default=False)
    approved = models.BooleanField(null=False, blank=True, default=True)

    date_added = models.DateField(auto_now_add=True, null=True, editable=False)
    last_changed = models.DateField(auto_now=True, null=True)
    primary_artist = models.BooleanField(
        null=False, blank=True, default=False,
        verbose_name="primary artist status"
    )

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
    title = models.CharField('Name', max_length=255, null=False)
    duration = models.DecimalField('Duration', null=True, blank=True, max_digits=6, decimal_places=2) # in seconds
    genre = models.CharField(max_length=255, null=True, blank=True)
    platform = models.CharField(max_length=255, null=True)
    is_explicit = models.BooleanField(null=False, blank=True, default=False)
    # tracks = one-to-many with 'Track'

    is_displayed = models.BooleanField(
        null=False, blank=True, default=True,
        verbose_name=_("display status")
    )
    is_deleted = models.BooleanField(
        null=False, blank=True, default=False,
        verbose_name=_("deletion status")
    )
    last_changed = models.DateField(auto_now=True, null=True, blank=True)
    uploaded_date = models.DateField(auto_now_add=True, null=True, blank=True, editable=False)

    album  = models.ForeignKey(Album, on_delete=models.CASCADE, null=False, blank=False)
    contributors = models.ManyToManyField(Artist, through='SongContributor', related_name="song_contributors")
    uploaded_by = models.ForeignKey(Artist, on_delete=models.SET_NULL, null=True, related_name="song_uploaded_by") # artist or user???
    tags = models.ManyToManyField(
        to='content.tag',
        related_name='songs'
    )

    objects = models.Manager() # all objects
    hidden_objects = NotDeletedManager() # objects that are not deleted
    display_objects = SongNotHiddenNotDeletedManager() # objects that are not deleted and not hidden and album is not hidden or deleted

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
    primary_artist = models.BooleanField(
        null=False, blank=True, default=False,
        verbose_name="primary artist status"
    )

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


class Tag(models.Model):
    text = models.CharField(
        max_length=100,
        primary_key=True,
        help_text=_("Text value of the tag"),
        verbose_name=_("Tag text")
    )
    # songs = many to many with 'Song'
    # albums = many to many with 'album'
    
    date_created = models.DateTimeField(
        auto_now_add=True,
        editable=False
    )
    last_changed = models.DateTimeField(
        auto_now=True
    )

    def __str__(self):
        return self.text
    
    def __repr__(self):
        return f"<{self.__class__.__name__} - {self.__str__()}>"


