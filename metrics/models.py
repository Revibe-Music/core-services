from django.conf import settings

from datetime import datetime
from pynamodb import models
from pynamodb.attributes import (
    UnicodeAttribute, NumberAttribute, UnicodeSetAttribute, UTCDateTimeAttribute, BooleanAttribute
)

from artist_portal._helpers import const


class Stream(models.Model):
    class Meta:
        table_name = const.STREAM_TABLE
        region = const.AWS_REGION
        aws_access_key_id = settings.AWS_ACCESS_KEY_ID
        aws_secret_access_key = settings.AWS_SECRET_ACCESS_KEY

    song_id = UnicodeAttribute(hash_key=True)
    user_id = UnicodeAttribute() # default 'opt-out' written in serializer
    timestamp = UTCDateTimeAttribute(default=datetime.now)
    stream_duration = NumberAttribute()
    stream_percentage = NumberAttribute()
    is_downloaded = BooleanAttribute(default=False)
    is_saved = BooleanAttribute(default=False)
    device = UnicodeAttribute()
    environment = UnicodeAttribute(default="production")
