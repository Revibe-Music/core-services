from django.conf import settings
from django.db import models
from django.utils.html import format_html
from django.utils.timezone import now
from django.utils.translation import gettext_lazy as _
import uuid

from logging import getLogger
logger = getLogger(__name__)

from revibe.utils.aws.s3 import delete_s3_object
from revibe.utils.classes import default_repr

from content import model_exts as ext
from content.managers import *

from utils.branch.utils import generate_canonical_identifier

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
    artistoftheweek = models.ForeignKey(
        to='administration.ArtistOfTheWeek',
        on_delete=models.CASCADE,
        related_name='images',
        null=True, blank=True,
        verbose_name=_("artist of the week"),
        help_text=_("Artist of the Week related object")
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

    def delete(self):
        delete_s3_object(self.file)
        super().delete()

    def __str__(self):
        name = '-no object-'
        if self.obj:
            if hasattr(self.obj, 'name'):
                name = self.obj.name
            elif hasattr(self.obj, 'artist'):
                name = self.obj.artist.name
        return f"{name} ({self.dimensions})"
    
    def __repr__(self):
        return default_repr(self)

    @property
    def obj(self):
        if self.artist:
            return self.artist
        elif self.album:
            return self.album
        elif self.artistoftheweek:
            return self.artistoftheweek
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
        null=True, blank=True
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

    def delete(self):
        """
        Delete the file object from S3 before removing the row from the db
        """
        delete_s3_object(self.file)
        super().delete()

    def __str__(self):
        try:
            ext = self.url.split('/')[-1]
            return f"{self.song.title} ({ext})"
        except Exception:
            return str(self.file)

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
    last_changed = models.DateTimeField(
        auto_now=True,
        null=True
    )

    @property
    def number_of_streams_from_uploads(self):
        """
        Count the number of streams from uploads
        """
        songs = getattr(self, 'song_uploaded_by').all()
        return songs.streams.all().count()

    @property
    def number_of_streams_from_contributions(self):
        """
        Count the number of streams from contributions
        """
        songs = getattr(self, 'song_contributors').all().distinct()
        return songs.streams.all().count()
    
    @property
    def number_of_streams(self):
        return self.number_of_streams_from_uploads + self.number_of_streams_from_contributions

    objects = models.Manager()
    display_objects = ArtistDisplayManager()

    def __str__(self):
        return "{}".format(self.name)
    
    def __repr__(self):
        return "<Artist: {} {}>".format(self.name, self.id)
    
    class Meta:
        verbose_name = 'artist'
        verbose_name_plural = 'artists'

    def _link_to_self(self):
        return format_html(
            "<a href='/{}content/artist/{}'>{}</a>",
            settings.ADMIN_PATH,
            self.id,
            self.__str__()
        )

    # branch stuff
    @property
    def canonical_identifier(self):
        platform = self.platform.lower()
        obj_type = 'artist'
        id = str(self.id)
        return generate_canonical_identifier(platform, obj_type, id)


class Album(models.Model):
    id = models.CharField(max_length=255, primary_key=True, default=uuid.uuid4, editable=False)
    uri = models.CharField(max_length=255, unique=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255, null=False)
    type = models.CharField(max_length=255, null=True, blank=True)
    platform = models.CharField(max_length=255, null=False, blank=False)
    # album_image = one-to-many with 'Image'

    uploaded_date = models.DateTimeField(auto_now_add=True, null=True, editable=False)
    last_changed = models.DateTimeField(auto_now=True, null=True)
    date_published = models.DateTimeField(null=True, blank=True, default=now)
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
    genres = models.ManyToManyField(
        to='content.genre',
        related_name='albums',
        blank=True
    )
    tags = models.ManyToManyField(
        to='content.tag',
        related_name='albums',
        help_text=_("Associated tags"),
        blank=True
    )

    objects = models.Manager()
    hidden_objects = NotDeletedManager()
    display_objects = AlbumNotHiddenNotDeletedManager()

    @property
    def number_of_streams(self):
        result = getattr(self, 'song_set').all().annotate(count_streams=models.Count('streams__id')).aggregate(models.Sum('count_streams'))
        return result["count_streams__sum"]

    def delete(self):
        songs = Song.objects.filter(album=self)
        for s in songs:
            s.delete()

        images = Image.objects.filter(album=self)
        for i in images:
            i.delete()

        self.is_displayed = False
        self.is_deleted = True
        self.save()

    def __str__(self):
        return "{}".format(self.name) + ("*" if self.is_deleted else "")

    def __repr__(self):
        return default_repr(self)

    class Meta:
        verbose_name = 'album'
        verbose_name_plural = 'albums'
        ordering = ['name',]

    # branch stuff
    @property
    def canonical_identifier(self):
        platform = self.platform.lower()
        obj_type = 'album'
        id = str(self.id)
        return generate_canonical_identifier(platform, obj_type, id)


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
    id = models.CharField(
        primary_key=True,
        max_length=255,
        editable=False, default=uuid.uuid4
    )
    uri = models.CharField(
        max_length=255,
        unique=True, editable=False, default=uuid.uuid4,
        verbose_name=_('URI'),
        help_text=_("Secondary unique identifier")
    )
    isrc_code = models.CharField(
        max_length=255,
        null=True, blank=True,
        verbose_name=_("ISRC code"),
        help_text=_("Internationally recognized identifier for the song")
    )
    title = models.CharField(
        max_length=255,
        null=False, blank=False,
        verbose_name=_("title")
    )
    duration = models.DecimalField(
        max_digits=6, decimal_places=2,
        null=True, blank=True,
        verbose_name=_("duration"),
        help_text=_("Duration of the song in seconds")
    ) # in seconds
    platform = models.CharField(
        max_length=255,
        null=True
    )
    is_explicit = models.BooleanField(
        null=False, blank=True, default=False
    )
    album_order = models.IntegerField(
        null=False, blank=True, default=0,
        verbose_name=_("order"),
        help_text=_("The order in which the songs will be displayed in the app.")
    )
    # tracks = one-to-many with 'Track'

    is_displayed = models.BooleanField(
        null=False, blank=True, default=True,
        verbose_name=_("display status")
    )
    is_deleted = models.BooleanField(
        null=False, blank=True, default=False,
        verbose_name=_("deletion status")
    )
    uploaded_date = models.DateTimeField(auto_now_add=True, null=True, blank=True, editable=False)
    last_changed = models.DateTimeField(auto_now=True, null=True, blank=True)

    album  = models.ForeignKey(Album, on_delete=models.CASCADE, null=False, blank=False)
    contributors = models.ManyToManyField(Artist, through='SongContributor', related_name="song_contributors")
    uploaded_by = models.ForeignKey(
        to=Artist,
        on_delete=models.SET_NULL,
        related_name="song_uploaded_by",
        null=True, blank=True
    )
    genres = models.ManyToManyField(
        to='content.genre',
        related_name='songs',
        blank=True
    )
    tags = models.ManyToManyField(
        to='content.tag',
        related_name='songs',
        blank=True
    )
    # streams = many-to-one with metrics.Stream

    objects = models.Manager() # all objects
    hidden_objects = NotDeletedManager() # objects that are not deleted
    display_objects = SongNotHiddenNotDeletedManager() # objects that are not deleted and not hidden and album is not hidden or deleted

    @property
    def number_of_streams(self):
        """
        Simple thing to make counting streams easier
        """
        return int(getattr(self, 'streams').all().count())

    def __str__(self):
        return "{}".format(self.title) + ("*" if self.is_deleted else "")
    
    def __repr__(self):
        return default_repr(self)
    
    def delete(self):
        tracks = self.tracks.all()
        for t in tracks:
            t.delete()
        self.is_displayed = False
        self.is_deleted = True
        self.save()
    
    class Meta:
        verbose_name = 'song'
        verbose_name_plural = 'songs'


    # branch stuff
    @property
    def canonical_identifier(self):
        platform = self.platform.lower()
        obj_type = 'song'
        id = str(self.id)
        return generate_canonical_identifier(platform, obj_type, id)


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
        return default_repr(self)


class PlaceholderContribution(models.Model):
    song = models.ForeignKey(
        to='content.song',
        on_delete=models.CASCADE,
        related_name='placeholder_contributions',
        null=True, blank=True,
        verbose_name=_('song'),
        help_text=_("The related song")
    )
    album = models.ForeignKey(
        to='content.album',
        on_delete=models.CASCADE,
        related_name='placeholder_contributions',
        null=True, blank=True,
        verbose_name=_("album"),
        help_text=_("The related album")
    )

    email = models.CharField(
        max_length=255,
        null=False, blank=False,
        verbose_name=_("email"),
        help_text=_("If an artist registers with this email, then will automatically create the contributions")
    )

    contribution_type = models.CharField(
        max_length=255,
        null=False, blank=False,
        verbose_name=_("contribution type"),
        help_text=_("the contribution type to be applied when creating the contribution")
    )

    date_created = models.DateTimeField(
        auto_now_add=True
    )

    class Meta:
        verbose_name = 'placeholder contribution'
        verbose_name_plural = 'placeholder contributions'

    def __str__(self):
        return self.email

    def __repr__(self):
        return f"<{self.__class__.__name__} ({self.__str__()})>"


class Genre(models.Model):
    text = models.CharField(
        max_length=255,
        null=False, blank=False,
        verbose_name=_("text"),
        help_text=_("The genre itself")
    )

    objects = GenreManager()

    def __str__(self):
        return self.text
    
    def __repr__(self):
        return default_repr(self)
    
    class Meta:
        verbose_name = "genre"
        verbose_name_plural = "genres"


# search stuff

class Search(models.Model):

    ALBUM = 'album'
    ARTIST = 'artist'
    GENRE = 'genre'
    SONG = 'song'
    TAG = 'tag'
    _model_choices = (
        (ALBUM, 'Album'),
        (ARTIST, 'Artist'),
        (GENRE, 'Genre'),
        (SONG, 'Song'),
        (TAG, 'Tag'),
    )
    model = models.CharField(
        max_length=100,
        choices=_model_choices,
        null=False, blank=False,
        verbose_name=_("model"),
        help_text=_("The model that is being searched.")
    )

    field = models.CharField(
        max_length=255,
        null=False, blank=False,
        verbose_name=_("search field"),
        help_text=_("The field to search for")
    )

    CONTAINS = 'contains'
    ICONTAINS = 'icontains'
    EXACT = 'exact'
    IEXACT = 'iexact'
    _type_choices = (
        (CONTAINS, 'Contains'),
        (ICONTAINS, 'Case-insensitive Contains'),
        (EXACT, 'Exact'),
        (IEXACT, 'Case-insensitive Exact')
    )
    type = models.CharField(
        max_length=100,
        choices=_type_choices,
        null=False, blank=False,
        verbose_name=_("search type"),
        help_text=_("The type of search to execute. See the docs for information on how each works.")
    )

    order = models.IntegerField(
        null=False, blank=False,
        verbose_name=_("order"),
        help_text=_("Order in which to execute the search function")
    )

    # extras
    active = models.BooleanField(
        null=False, blank=False, default=True,
        verbose_name=_("active"),
        help_text=_("Enables/disables the search field.")
    )
    description = models.TextField(
        null=True, blank=True,
        verbose_name=_("description"),
        help_text=_("Human-readable explanation of the search field")
    )
    date_created = models.DateTimeField(
        auto_now_add=True
    )
    last_changed = models.DateTimeField(
        auto_now=True
    )

    objects = SearchManager()

    def __str__(self):
        return self.field

    def __repr__(self):
        return default_repr(self)

    class Meta:
        verbose_name = "search field"
        verbose_name_plural = "search fields"


class AlbumSearch(Search):
    objects = AlbumSearchManager()

    def __init__(self, *args, **kwargs):
        self._meta.get_field('model').default = self.ALBUM
        super().__init__(*args, **kwargs)

    class Meta:
        proxy = True
        verbose_name = "album search field"
        verbose_name_plural = "album search fields"


class ArtistSearch(Search):
    objects = ArtistSearchManager()

    def __init__(self, *args, **kwargs):
        self._meta.get_field('model').default = self.ARTIST
        super().__init__(*args, **kwargs)

    class Meta:
        proxy = True
        verbose_name = "artist search field"
        verbose_name_plural = "artist search fields"


class GenreSearch(Search):
    objects = GenreSearchManager()

    def __init__(self, *args, **kwargs):
        self._meta.get_field('model').default = self.GENRE
        super().__init__(*args, **kwargs)

    class Meta:
        proxy = True
        verbose_name = "genre search field"
        verbose_name_plural = "genre search fields"


class SongSearch(Search):
    objects = SongSearchManager()

    def __init__(self, *args, **kwargs):
        self._meta.get_field('model').default = self.SONG
        super().__init__(*args, **kwargs)

    class Meta:
        proxy = True
        verbose_name = "song search field"
        verbose_name_plural = "song search fields"


class TagSearch(Search):
    objects = TagSearchManager()

    def __init__(self, *args, **kwargs):
        self._meta.get_field('model').default = self.TAG
        super().__init__(*args, **kwargs)

    class Meta:
        proxy = True
        verbose_name = "tag search field"
        verbose_name_plural = "tag search fields"


