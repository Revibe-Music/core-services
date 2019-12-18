from datetime import datetime
from pynamodb import models
from pynamodb.attributes import (
    UnicodeAttribute, NumberAttribute, UnicodeSetAttribute, UTCDateTimeAttribute, BooleanAttribute
)


# class Streams(models.Model):
#     song = models.ForeignKey('music.Song', on_delete=models.CASCADE, related_name='song_streams', null=False, blank=False)
#     user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name="user_streams", on_delete=models.SET_NULL, null=True, blank=False)
#     timestamp = models.DateTimeField(auto_now_add=True, null=False, editable=False)
#     stream_duration = models.IntegerField()
#     stream_percentage = models.DecimalField()
#     is_downloaded = models.BooleanField()
#     is_saved = models.BooleanField()
#     device = models.CharField(max_length=255)


class Stream(models.Model):
    class Meta:
        table_name = 'Stream'
        region = 'us-east-2'

    song = UnicodeAttribute(hash_key=True)
    user = UnicodeAttribute(range_key=True)
    timestamp = UTCDateTimeAttribute(default=datetime.now)
    stream_duration = NumberAttribute()
    stream_percentage = NumberAttribute()
    is_downloaded = BooleanAttribute(default=False)
    is_saved = BooleanAttribute(default=False)
    device = UnicodeAttribute()
