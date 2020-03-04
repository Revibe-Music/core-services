"""
Created: 4 Mar. 2020
Author: Jordan Prechac
"""

from django.urls import reverse

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
            "kwargs": {"time_period": "today", "limit": browse_page_limit}
        },
        {
            "function": sections.trending_albums,
            "kwargs": {"time_period": "today", "limit": browse_page_limit}
        },
        {
            "function": sections.trending_artists,
            "kwargs": {"time_period": "today", "limit": browse_page_limit}
        },
        {
            # Popular Youtube songs on Revibe
            "function": sections.treding_youtube_videos,
            "kwargs": {"time_period": "last_week", "limit": browse_page_limit}
        },
        # TODO: recently uploaded albums
    ]
    for func in browses:
        function_result = func["function"](**func["kwargs"])
        if bool(function_result["results"]):
            output.append(function_result)

    # top hits are always available at the bottom of the browse page
    output.append({
        "name": "Top Hits - All-Time",
        "type": "container",
        "results": [
            {
                "name": "Top Songs",
                "type": "songs",
                "icon": None,
                "url": reverse("browse-top-songs-all-time"),
            },
            {
                "name": "Top Albums",
                "type": "albums",
                "icon": None,
                "url": reverse("browse-top-albums-all-time"),
            },
            {
                "name": "Top Artists",
                "type": "artists",
                "icon": None,
                "url": reverse("browse-top-artists-all-time"),
            },
        ],
    })

    return output
