"""
Created: 02 June 2020
Author: Jordan Prechac
"""

from django.db.models import Count

import datetime

from accounts.models import CustomUser
from administration.utils import retrieve_variable
from metrics.models import Stream
from notifications.exceptions import NotificationException
from notifications.models import TemporalEvent

from notifications.core.notifier import Notifier

# -----------------------------------------------------------------------------

def send_artist_recap_email(user, weeks=1):
    email = user.profile.email
    if not email:
        raise NotificationException(f"User '{user}' does not have an email")
    if not user.is_artist:
        raise NotificationException(f"User '{user}' is not an artist")
    artist = user.artist

    # check the user's message notifications
    required_settings = [
        (user.profile.allow_email_reminders, True),
        (user.profile.allow_email_notifications, True),
    ]
    for setting in required_settings:
        if setting[0] != setting[1]:
            return


    # calculate the artist's analytics info
    _days = weeks*7
    now = datetime.datetime.now()
    one_week = now - datetime.timedelta(days=_days)
    two_weeks = now - datetime.timedelta(days=_days)

    # # get the % change in streams from last week to this week
    streams = Stream.objects.filter(song__in=artist.song_uploaded_by.all())
    old_streams = streams.filter(
        timestamp__gte=two_weeks,
        timestamp__lte=one_week
    )
    old_streams_count = old_streams.count()
    new_streams = streams.filter(
        timestamp__gte=one_week,
        timestamp__lte=now
    )
    new_streams_count = new_streams.count()

    old_streams_count = old_streams_count if old_streams_count else 1

    stream_change = (new_streams_count - old_streams_count) / old_streams_count
    stream_change_percent = stream_change * 100
    stream_change_percent_formatted = f"{round(stream_change_percent, 0)}%"

    # # get the % change in listeners from last week to this week
    old_listeners = old_streams.aggregate(
        sum_users=Count('user', distinct=True)
    )['sum_users']
    new_listeners = new_streams.aggregate(
        sum_users=Count('user', distinct=True)
    )['sum_users']

    old_listeners = old_listeners if old_listeners else 1

    listeners_change = (new_listeners - old_listeners) / old_listeners
    listeners_change_percent = listeners_change * 100
    listeners_change_percent_formatted = f"{round(listeners_change_percent, 0)}%"
    print("New Listeners", new_listeners)
    print("Old listeners", old_listeners)
    print("Change", listeners_change_percent_formatted)


    # configure the email with the analytics info
    context = {
        "stream_change": stream_change,
        "stream_change_percent": stream_change_percent,
        "stream_change_percent_formatted": stream_change_percent_formatted,
        "listeners_change": listeners_change,
        "listeners_change_percent": listeners_change_percent,
        "listeners_change_percent_formatted": listeners_change_percent_formatted,
    }

    # tell the Notifier to send the email
    notifier = Notifier(
        user, 'temporal-artist-recap-email',
        artist=True, force=True,
        extra_configs=context
    )
    return notifier.send()



