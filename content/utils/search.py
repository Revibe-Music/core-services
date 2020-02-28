from django.db.models import Count, Q

from revibe._helpers import const
from revibe.platforms import Revibe

# -----------------------------------------------------------------------------

limit = const.SEARCH_LIMIT

def _generate_q(text, *args):
    # get list from *args, or just get the embedded list
    args = args[0] if isinstance(args[0], list) else [x for x in args]

    kwargs = {key: text for key in args}

    return Q(**kwargs)


def search_songs(text, *args, **kwargs):
    platform = Revibe()

    def attach_new_songs(filtr):
        _count_annotation = Count('streams__id')
        return platform.Songs.filter(filtr).distinct().annotate(count=_count_annotation).order_by('-count')

    base_filter = _generate_q(text, "title__iexact")
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
        filtr = _generate_q(text, filters.pop(0))
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
    
    base_filter = _generate_q(text, 'name__iexact')
    filters = [
        "uploaded_by__name__iexact",
        "contributors__name__iexact",
        "song__title__iexact",
        "name__icontains",
        "uploaded_by__name__icontains",
        "contributors__name__icontains",
        "contributors__name__icontains",
        "song__title__icontains"
    ]

    albums = attach_new_albums(base_filter)
    while albums.count() < limit and len(filters) > 0:
        filtr = _generate_q(text, filters.pop(0))
        albums = albums | attach_new_albums(filtr)
        albums = albums.distinct()
    
    return albums[:limit]


def search_artists(text, *args, **kwargs):
    platform = Revibe()

    def attach_new_artists(filtr):
        _count_annotation = Count("song_uploaded_by__streams__id")
        return platform.Artists.filter(filtr).distinct().annotate(count=_count_annotation).order_by("-count")
    
    base_filter = _generate_q(text, "name__iexact")
    filters = [
        ["song_uploaded_by__title__iexact", "album__name__iexact"],
        "name__icontains",
        ["song_uploaded_by__title__icontains", "album__name__icontains"],
    ]

    artists = attach_new_artists(base_filter)
    while artists.count() < limit and len(filters) > 0:
        filtr = _generate_q(text, filters.pop(0))
        print(f"Artist filter: {filtr}")
        artists = artists | attach_new_artists(filtr)
        artists = artists.distinct()
    
    return artists[:limit]


def search_playlists(text, *args, **kwargs):
    pass

