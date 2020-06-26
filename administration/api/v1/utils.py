"""
Created: 26 June 2020
"""

from django.apps import apps
from django.db.models import Q, Count

import datetime

# -----------------------------------------------------------------------------

Artist = apps.get_model('content', 'Artist')
Stream = apps.get_model('metrics', 'Stream')


def get_all_listen_for_change():
    """
    Get all the streams from the listen for change event


    Computation steps:
    1. define start and end dates
    2. Create the stream filter(s)
    3. aggregate the streams
    """

    # 1
    start_date = datetime.date(year=2020, month=6, day=22)
    end_date = datetime.date(year=2020, month=6, day=28)

    # 2
    stream_song_filter = Q(song__platform='Revibe')
    stream_time_filter = Q(timestamp__gte=start_date, timestamp__lte=end_date)

    # 3
    streams = Stream.objects.filter(stream_song_filter, stream_time_filter)
    stream_count = streams.aggregate(num_streams=Count('id'))

    return stream_count

