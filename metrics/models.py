from django.conf import settings
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from datetime import datetime
from pynamodb import models as pynamo_models
from pynamodb.attributes import (
    UnicodeAttribute, ListAttribute, 
)

from revibe._helpers import const
from revibe.utils.classes import default_repr

# -----------------------------------------------------------------------------

class Stream(models.Model):

    # choices
    _library_choice = 'library'
    _playlist_choice = 'playlist'
    _search_choice = 'search'
    _browse_choice = 'browse'
    _album_choice = 'album'
    _artist_choice = 'artist'
    _share_choice = 'share'
    _embedded_choice = 'embedded'

    _source_choices = (
        (_library_choice, 'Library'),
        (_playlist_choice, 'Playlist'),
        (_search_choice, 'Search'),
        (_browse_choice, 'Browse'),
        (_album_choice, 'Album Page'),
        (_artist_choice, 'Artist Page'),
        (_share_choice, 'Shared'),
        (_embedded_choice, 'Embedded Player'),
    )

    id = models.AutoField(
        primary_key=True
    )
    song = models.ForeignKey(
        to='content.song',
        related_name='streams',
        on_delete=models.CASCADE,
        null=True, blank=True,
        verbose_name=_("song"),
        help_text=_("The song that was streamed")
    )
    alternate_id = models.CharField(
        max_length=255,
        null=True, blank=True, default=None,
        verbose_name=_("alternate ID"),
        help_text=_("ID of the song/video streamed if that ID has not yet been stored in the database")
    )
    alternate_platform = models.CharField(
        max_length=255,
        null=True, blank=True, default=None,
        verbose_name=_("alternate platform"),
        help_text=_("Platform of the song/video if that song/video has not yet been stored in the database")
    )
    user = models.ForeignKey(
        to='accounts.customuser',
        related_name='streams',
        on_delete=models.SET_NULL,
        null=True, blank=True,
        verbose_name=_("user"),
        help_text=_("The user that streamed the song")
    )
    timestamp = models.DateTimeField(
        auto_now_add=True
    )
    stream_duration = models.DecimalField(
        null=True, blank=True,
        max_digits=8, decimal_places=2,
        verbose_name=_("stream duration"),
        help_text=_("The length of time the user streamed the song for")
    )
    is_downloaded = models.BooleanField(
        null=True, blank=True,
        verbose_name=_("download status"),
        help_text=_("Whether or not the user has the song downloaded")
    )
    is_saved = models.BooleanField(
        null=True, blank=True,
        verbose_name=_("saved status"),
        help_text=_("Whether or not the user has the song saved in their library at the time of streaming the song")
    )
    source = models.CharField(
        max_length=255,
        choices=_source_choices,
        null=True, blank=True,
        verbose_name=_("stream source"),
        help_text=_("Source the user streamed the song from: playlist, search, etc.")
    )

    # location data
    lat = models.DecimalField(
        max_digits=9, decimal_places=6,
        null=True, blank=True,
        verbose_name=_("latitude")
    )
    long = models.DecimalField(
        max_digits=9, decimal_places=6,
        null=True, blank=True,
        verbose_name=_("longitude")
    )

    def __str__(self):
        first_part = self.song.title if self.song else f"<{self.alternate_id}>"
        return f"{first_part} | {self.user.username if self.user else self.timestamp}"

    def __repr__(self):
        return f"<{self.__class__.__name__} ({self.id})>"

    class Meta:
        verbose_name = "stream"
        verbose_name_plural = "streams"


class Search(models.Model):

    search_text = models.TextField(
        null=False, blank=False,
        verbose_name=_("search text"),
        help_text=_("The search query")
    )
    user = models.ForeignKey(
        to='accounts.customuser',
        on_delete=models.SET_NULL,
        related_name='searches',
        null=True, blank=True,
        verbose_name=_("user"),
        help_text=_("The user that searched something")
    )
    timestamp = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return self.search_text

    def __repr__(self):
        return f"<{self.__class__.__name__} ({self.search_text})>"

    class Meta:
        verbose_name = _("search")
        verbose_name_plural = _("searches")


class AppSession(models.Model):

    start_time = models.DateTimeField(
        auto_now_add=True
    )
    end_time = models.DateTimeField(
        auto_now=True
    )
    user = models.ForeignKey(
        to='accounts.customuser',
        on_delete=models.CASCADE,
        related_name='sessions',
        null=False, blank=False,
        verbose_name=_("user"),
        help_text=_("User that sessioned")
    )
    interactions = models.IntegerField(
        null=False, blank=True, default=0,
        verbose_name=_("interactions"),
        help_text=_("Number of interactions the user had with the app during the session")
    )

    @property
    def session_time(self):
        tdelta = self.end_time - self.start_time
        minutes = tdelta.total_seconds() / 60

        return minutes

    class Meta:
        verbose_name = _("mobile app session")
        verbose_name_plural = _("mobile app sessions")


class ArtistPublicURLClick(models.Model):

    artist = models.ForeignKey(
        to='content.artist',
        on_delete=models.SET_NULL,
        related_name='url_clicks',
        limit_choices_to={'platform': 'Revibe'},
        null=True, blank=True,
        verbose_name=_("artist"),
        help_text=_("Artist whose page was clicked on")
    )
    timestamp = models.DateTimeField(
        auto_now_add=True
    )

    def __repr__(self):
        return default_repr(self)
    
    class Meta:
        verbose_name = "artist public URL click"
        verbose_name_plural = "artist public URL clicks"


# -----------------------------------------------------------------------------

class Request(pynamo_models.Model):
    class Meta:
        table_name = const.REQUEST_TABLE
        region = const.AWS_REGION
        aws_access_key_id = settings.AWS_ACCESS_KEY_ID
        aws_secret_access_key = settings.AWS_SECRET_ACCESS_KEY
    
    url = UnicodeAttribute(hash_key=True)
    requests = ListAttribute()


# -----------------------------------------------------------------------------
# DEPRECATED
# Used to use AWS DynamoDB for tracking stream information

# class Stream(models.Model):
#     class Meta:
#         table_name = const.STREAM_TABLE
#         region = const.AWS_REGION
#         aws_access_key_id = settings.AWS_ACCESS_KEY_ID
#         aws_secret_access_key = settings.AWS_SECRET_ACCESS_KEY

#     song_id = UnicodeAttribute(hash_key=True)
#     user_id = UnicodeAttribute() # default 'opt-out' written in serializer
#     timestamp = UTCDateTimeAttribute(default=datetime.now)
#     stream_duration = NumberAttribute()
#     stream_percentage = NumberAttribute()
#     is_downloaded = BooleanAttribute(default=False)
#     is_saved = BooleanAttribute(default=False)
#     device = UnicodeAttribute()
#     environment = UnicodeAttribute(default="production")


