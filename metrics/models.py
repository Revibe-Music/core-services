from datetime import datetime
from pynamodb import models
from pynamodb.attributes import (
    UnicodeAttribute, NumberAttribute, UnicodeSetAttribute, UTCDateTimeAttribute, BooleanAttribute
)


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
