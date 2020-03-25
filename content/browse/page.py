"""
Created: 4 Mar. 2020
Author: Jordan Prechac
"""

import logging
logger = logging.getLogger(__name__)

from . import sections

# -----------------------------------------------------------------------------

def full_browse_page():
    output = []

    # time_period = get_url_param(request.query_params, "time_period")
    # if time_period == None:
    #     time_period = "today"

    # append various browse things
    browse_page_limit = 5
    browses = [
        {
            "function": sections.artist_spotlight,
            "kwargs": {},
        },
        {
            "function": sections.trending_songs,
            "kwargs": {"limit": browse_page_limit}
        },
        {
            "function": sections.trending_albums,
            "kwargs": {"limit": browse_page_limit}
        },
        {
            "function": sections.trending_artists,
            "kwargs": {"limit": browse_page_limit}
        },
        {
            # Popular Youtube songs on Revibe
            "function": sections.treding_youtube_videos,
            "kwargs": {"time_period": "last_week", "limit": browse_page_limit}
        },
        {
            # TODO: recently uploaded albums
            "function": sections.recently_uploaded_albums,
            "kwargs": {"time_period": "last_week", "limit": browse_page_limit}
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
