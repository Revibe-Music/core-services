"""
Created: 24 June 2020
"""

from django.apps import apps
from django.db import models
from django.db.models import Q, Count

import datetime

# -----------------------------------------------------------------------------

Artist = apps.get_model('content', 'Artist')
Stream = apps.get_model('metrics', 'Stream')


def get_artist_listen_for_change_streams(artist: Artist=None):
    """
    Computation steps:

    1. Define start and end dates
    2. Create stream filters for the current artist
    3. aggregate the streams from the Model
    4. Return just the number (maybe a dict idk)
    """
    # Validate argument data types
    if not isinstance(artist, Artist): raise TypeError("Param 'artist' must be an Artist object")

    # 1
    start_date = datetime.date(year=2020, month=6, day=22)
    end_date = datetime.date(year=2020, month=6, day=28)

    # 2
    stream_song_filter = Q(song__uploaded_by=artist)
    stream_time_filter = Q(timestamp__gte=start_date, timestamp__lte=end_date)

    # 3
    streams = Stream.objects.filter(stream_song_filter, stream_time_filter)
    stream_count = streams.aggregate(num_streams=Count('id'))

    return stream_count








