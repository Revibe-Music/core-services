"""
Created: 4 Mar. 2020
Author: Jordan Prechac
"""

import logging
logger = logging.getLogger(__name__)

from . import sections

from administration.utils import retrieve_variable

# -----------------------------------------------------------------------------

def full_browse_page():
    output = []

    # get time period
    default_time_period = "last_week"
    time_period = retrieve_variable("browse_time_period", default_time_period)
    if time_period != sections.time_lookup.keys():
        time_period = default_time_period

    # get limit of items
    default_browse_page_limit = 5
    try:
        browse_page_variable = int(retrieve_variable("browse_page_limit", default_browse_page_limit))
    except ValueError:
        browse_page_variable = default_browse_page_limit

    browse_page_limit = max(min(browse_page_variable, 10), 2)


    # append various browse things
    browses = [
        {
            "function": sections.artist_spotlight,
            "kwargs": {},
        },
        {
            "function": sections.trending_songs,
            "kwargs": {"time_period": time_period, "limit": browse_page_limit}
        },
        {
            "function": sections.trending_albums,
            "kwargs": {"time_period": time_period, "limit": browse_page_limit}
        },
        {
            "function": sections.trending_artists,
            "kwargs": {"time_period": time_period, "limit": browse_page_limit}
        },
        {
            # Popular Youtube songs on Revibe
            "function": sections.treding_youtube_videos,
            "kwargs": {"time_period": time_period, "limit": browse_page_limit}
        },
        {
            # TODO: recently uploaded albums
            "function": sections.recently_uploaded_albums,
            "kwargs": {"time_period": time_period, "limit": browse_page_limit}
        },
        {
            # Revibe-curated playlists
            "function": sections.revibe_curated_playlists,
            "kwargs": {"limit": browse_page_limit},
        },
        {
            "function": sections.top_content_container,
            "kwargs": {}
        },
    ]
    for func in browses:
        try:
            function_result = func["function"](**func["kwargs"])
            if bool(function_result["results"]):
                output.append(function_result)
        except Exception as e:
            logger.warn(e)

    return output
