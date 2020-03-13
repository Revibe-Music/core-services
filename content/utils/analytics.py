"""
Created: 13 Mar. 2020
Author: Jordan Prechac
"""

from content.models import Song
from metrics.models import Stream

# -----------------------------------------------------------------------------


def calculate_advanced_song_analytics(song):
    """
    """
    output = {}

    # get unique monthly listeners
    # output['unique_monthly_listeners'] = Stream.objects.filter(song=song)

    return output

