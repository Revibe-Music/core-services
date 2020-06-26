from django.apps import apps
from django.db import models
from django.db.models import Q, Count

import datetime

Artist = apps.get_model('content', 'Artist')
Stream = apps.get_model('metrics', 'Stream')

def get_artist_listen_for_change_streams(artist: Artist=None):
    """
    define start and end dates
    create stream filters for current artist, aggregate streams from model, return just the num
    """
    if not isinstance(artist, Artist): raise TypeError('Param artist must be an Artist obj')
    # test that it includes streams from start and end date
    start_date = datetime.date(year=2020, month=6, day=22)
    end_date = datetime.date(year=2020, month=6, day=28)

    stream_song_filter = Q(song__uploaded_by=artist)
    stream_time_filter = Q(timestamp__gte=start_date, timestamp__lte=end_date)

    streams = Stream.objects.filter(stream_song_filter, stream_time_filter)
    stream_count = streams.aggregate(num_streams=Count('id'))

    return stream_count


