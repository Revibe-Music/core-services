from django.conf import settings
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from datetime import datetime

from revibe._helpers import const

# -----------------------------------------------------------------------------

class Stream(models.Model):
    id = models.AutoField(
        primary_key=True
    )
    song = models.ForeignKey(
        to='content.song',
        related_name='streams',
        on_delete=models.CASCADE,
        null=False, blank=False,
        verbose_name=_("song"),
        help_text=_("The song that was streamed")
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

    def __str__(self):
        return f"{self.song.title} - {self.user.username if self.user else self.timestamp}"
    
    def __repr__(self):
        return f"<{self.__class__.__name__} ({self.id})>"

    class Meta:
        verbose_name = "stream"
        verbose_name_plural = "streams"


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


