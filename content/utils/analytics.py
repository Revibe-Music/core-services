"""
Created: 13 Mar. 2020
Author: Jordan Prechac
"""

from django.db.models import Count

from revibe.contrib.queries.functions import Month, Year

from content.models import Song
from metrics.models import Stream

# -----------------------------------------------------------------------------


def calculate_advanced_song_analytics(song):
    """
    """
    output = {}
    streams = Stream.objects.filter(song=song)

    # get unique monthly listeners
    output['monthly_streams'] = streams.annotate(
        year=Year('timestamp'),
        month=Month('timestamp')
    ).values('year','month').annotate(count=Count('id'))

    return output

