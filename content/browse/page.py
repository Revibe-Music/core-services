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
            "variable": "browse_artist_spotlight",
        },
        {
            "function": sections.trending_songs,
            "kwargs": {"time_period": time_period, "limit": browse_page_limit},
            "variable": "browse_trending_songs",
        },
        {
            "function": sections.trending_albums,
            "kwargs": {"time_period": time_period, "limit": browse_page_limit},
            "variable": "browse_trending_albums",
        },
        {
            "function": sections.trending_artists,
            "kwargs": {"time_period": time_period, "limit": browse_page_limit},
            "variable": "browse_trending_artists",
        },
        {
            # Popular Youtube songs on Revibe
            "function": sections.trending_youtube,
            "kwargs": {"time_period": time_period, "limit": browse_page_limit},
            "variable": "browse_treding_youtube_videos",
        },
        {
            # TODO: recently uploaded albums
            "function": sections.recently_uploaded_albums,
            "kwargs": {"time_period": time_period, "limit": browse_page_limit},
            "variable": "browse_recently_uploaded_albums",
        },
        {
            # Revibe-curated playlists
            "function": sections.revibe_playlists,
            "kwargs": {"limit": browse_page_limit},
            "variable": "browse_curated_playlists",
        },
        {
            "function": sections.top_content_container,
            "kwargs": {},
            "variable": "browse_top_content",
        },
    ]
    for func in browses:
        # skip this section if the admin variable says to skip it
        if 'variable' in func.keys():
            run = retrieve_variable(func.get('variable'), True, is_bool=True)
            print(run)
            if not run:
                continue

        try:
            function_result = func["function"](**func["kwargs"])
            if bool(function_result["results"]):
                output.append(function_result)
        except Exception as e:
            logger.warn(e)

    return output
