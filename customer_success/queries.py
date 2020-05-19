"""
Created: 18 May 2020
Author: Jordan Prechac
"""

from django.db import models
from django.db.models import F, Q

import datetime

from accounts.models import CustomUser

# -----------------------------------------------------------------------------


def user_query():
    now   =       datetime.datetime.now()
    week  = now - datetime.timedelta(days=7)
    month = now - datetime.timedelta(days=30)
    year  = now - datetime.timedelta(days=365)

    stream_annotations = {
        "num_streams": models.Count('streams', distinct=True),
        "num_streams_week": models.Count('streams__id', filter=Q(streams__timestamp__gte=week), distinct=True),
        "num_streams_month": models.Count('streams__id', filter=Q(streams__timestamp__gte=month), distinct=True),
        "num_streams_year": models.Count('streams__id', filter=Q(streams__timestamp__gte=year), distinct=True),
    }
    search_annotations = {
        "num_searches": models.Count('searches', distinct=True),
        "num_searches_week": models.Count('searches__id', filter=Q(searches__timestamp__gte=week), distinct=True),
        "num_searches_month": models.Count('searches__id', filter=Q(searches__timestamp__gte=month), distinct=True),
        "num_searches_year": models.Count('searches__id', filter=Q(searches__timestamp__gte=year), distinct=True),
    }

    profile_fields = ['allow_explicit', 'skip_youtube_when_phone_is_locked', 'allow_listening_data', 'allow_search_data', 'allow_donation_data', 'allow_email_marketing', 'allow_email_notifications']
    profile_annotations = {thing: F(f"profile__{thing}") for thing in profile_fields}

    user_query = CustomUser.objects.filter(
            programmatic_account=False
        ).annotate(
            # get the streaming numbers
            **stream_annotations
        ).annotate(
            # get the search numbers
            **search_annotations
        ).annotate(
            # extra profile information
            **profile_annotations
        )
    
    fields = ['last_login', 'is_staff', 'is_active', 'date_joined', 'is_artist', 'is_manager', 'log_in_mobile_app', 'log_in_artist_portal', 'temporary_account']
    dicts = [stream_annotations, search_annotations, profile_annotations]
    for d in dicts:
        fields += d.keys()
    
    print(fields)
    print(type(fields))

    return user_query.values(*fields)


