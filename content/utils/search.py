from django.db.models import Count, Q

from revibe._helpers import const
from revibe.platforms import Revibe

# -----------------------------------------------------------------------------

limit = const.SEARCH_LIMIT

def _generate_q(kwarg, text):
    return Q(**{kwarg: text})

def search_songs(text, *args, **kwargs):
    platform = Revibe()

    def attach_new_songs(filtr):
        _count_annotation = Count('streams__id')
        return platform.Songs.filter(filtr).distinct().annotate(count=_count_annotation).order_by('-count')

    base_filter = Q(title__iexact=text)
    filters = [
        "uploaded_by__name__iexact",
        "contributors__name__iexact",
        "album__name__iexact",
        "title__icontains",
        "uploaded_by__name__icontains",
        "contributors__name__icontains",
        "album__name__icontains",
        "album__contributors__name__iexact",
        "album__contributors__name__icontains",
    ]

    # print(f"Beginning song search loop with {songs.count()} songs...")
    songs = attach_new_songs(base_filter)
    while songs.count() < limit and len(filters) > 0:
        filtr = _generate_q(filters.pop(0), text)
        songs = songs | attach_new_songs(filtr)
        songs = songs.distinct()
        # print(f"Ending iteration with filter '{filtr}'. Added {songs.count()} songs.")
    # print(f"Ending loop with {songs.count()} songs found.")

    return songs[:limit]


def search_albums(text, *args, **kwargs):
    platform = Revibe()

    def attach_new_albums(filtr):
        _count_annotation = Count('song__streams__id')
        return platform.Albums.filter(filtr).distinct().annotate(count=_count_annotation).order_by('-count')
    
    base_filter = _generate_q('name__iexact', text)
    filters = [
        "uploaded_by__name__iexact",
        "contributors__name__iexact",
    ]

def search_artists(text, *args, **kwargs):
    pass

def search_playlists(text, *args, **kwargs):
    pass

