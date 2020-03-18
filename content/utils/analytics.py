"""
Created: 13 Mar. 2020
Author: Jordan Prechac
"""

from django.db.models import Avg, Count, Q

from revibe.contrib.queries.functions import Month, Year

from accounts.models import CustomUser
from content.models import Song
from metrics.models import Stream

# -----------------------------------------------------------------------------

def song_unique_monthly_listeners(song, aggregate=False):
    """
    """
    numbers = Stream.objects.filter(song=song) \
        .distinct() \
        .annotate(
            year=Year('timestamp'),
            month=Month('timestamp')
        ) \
        .values('year', 'month') \
        .distinct() \
        .order_by('year', 'month') \
        .annotate(count=Count('user', distinct=True))
    
    if not aggregate:
        return numbers
    else:
        return numbers.aggregate(avg=Avg('count'))['avg']

def calculate_advanced_song_analytics(song):
    """
    """
    output = {}
    streams = Stream.objects.filter(song=song)

    # monthly streams
    output['monthly_streams'] = streams.annotate(
        year=Year('timestamp'),
        month=Month('timestamp')
    ).values('year','month').annotate(count=Count('id'))

    # unique monthly listeners
    output['unique_monthly_listeners'] = song_unique_monthly_listeners(song, aggregate=False)

    return output


def calculate_unique_monthly_listeners(artist, include_contributions=True, split_contributions=False, aggregate=False):
    """
    Computes the average unique monthly listeners of an artist.

    Computation steps/logic
    1. Get users that streamed a song uploaded by this artist
    2. Make that list distinct
    3. Calculate that for each month & year in the stream table
    4. Avg. out those month & year grouped numbers

    Arguments
    ---------
    artist: (<Artist>) the artist to calculate this on
    include_contributions: (bool) whether or not to include songs the artist contributed to but did not upload
    split_contributions: (bool) split the final results between uploads and contributions. Can only be True if include_contributions is True
    aggregate: (bool) whether to calculate an average of all the months found, or to return all the time-series data

    Examples
    --------
    >>> 

    """
    # check inputs
    if include_contributions == False:
        split_contributions = False

    # define possible filters
    filter_song_upload = {"song__in": artist.song_uploaded_by.all()}
    filter_song_contrib = {"song__in": artist.song_contributors.all()}

    # decide the stream filter
    stream_filter = Q(**filter_song_upload)

    count_annotation = {
        "user_count": Count('user', distinct=True)
    } 

    if include_contributions:
        stream_filter = stream_filter | Q(**filter_song_contrib)

        # if split_contributions:
        #     count_annotation = {
        #         "user_count": Count('user', filter=Q(filter_song_upload), distinct=True),
        #         "user_count_contributions": Count('user', filter=Q(filter_song_contrib), distinct=True)
        #     }


    # query
    user_numbers = Stream.objects \
    .filter(stream_filter) \
    .distinct()\
    .annotate(
        year=Year('timestamp'),
        month=Month('timestamp')
    ) \
    .values('year', 'month') \
    .distinct() \
    .order_by('year', 'month') \
    .annotate(**count_annotation)

    if not aggregate:
        return user_numbers
    else:
        # if split_contributions:
        #     return user_numbers.aggregate(user_avg=Avg('user_count'), user_avg_contrib=Avg('user_count_contributions'))
        # else:
        return user_numbers.aggregate(user_avg=Avg('user_count'))

