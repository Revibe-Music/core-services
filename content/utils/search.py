from django.db.models import Count, Q

from administration.utils import retrieve_variable
from content.search.utils import generate_search_field_text
from content.models import AlbumSearch, ArtistSearch, SongSearch

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


    # get the search fields from the database
    filter_objects = SongSearch.objects.filter(active=True)
    enough_filters = filter_objects.count() >= retrieve_variable('search-songs-minimum_filters', 3, output_type=int)

    if enough_filters:
        base_filter = _generate_q(text, generate_search_field_text(filter_objects.first()))
        filters = [ generate_search_field_text(f) for f in filter_objects[1:] ]
    else:
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

    songs = attach_new_songs(base_filter)
    while songs.count() < limit and len(filters) > 0:
        filtr = _generate_q(text, filters.pop(0))
        songs = songs | attach_new_songs(filtr)
        songs = songs.distinct()

    return songs[:limit]


def search_albums(text, *args, **kwargs):
    platform = Revibe()

    def attach_new_albums(filtr):
        _count_annotation = Count('song__streams__id')
        return platform.Albums.filter(filtr).distinct().annotate(count=_count_annotation).order_by('-count')

    filter_objects = AlbumSearch.objects.filter(active=True)
    enough_filters = filter_objects.count() >= retrieve_variable('search-albums-minimum_filters', 3, output_type=int)

    if enough_filters:
        # generate the filters list
        base_filter = _generate_q(text, generate_search_field_text(filter_objects.first()))
        filters = [ generate_search_field_text(f) for f in filter_objects[1:] ]
    else:
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

    # get the search fields from the database
    filter_objects = ArtistSearch.objects.filter(active=True)
    enough_filters = filter_objects.count() >= retrieve_variable('search-artists-minimum_filters', 2, output_type=int)

    if enough_filters:
        # if there are enough db filters, use them
        base_filter = _generate_q(text, generate_search_field_text(filter_objects.first()))
        filters = [ generate_search_field_text(f) for f in filter_objects[1:] ]
    else:
        # if there aren't enough db filters, use the defaults
        base_filter = _generate_q(text, "name__iexact")
        filters = [
            ["song_uploaded_by__title__iexact", "album__name__iexact"],
            "name__icontains",
            ["song_uploaded_by__title__icontains", "album__name__icontains"],
        ]

    artists = attach_new_artists(base_filter)

    # loop through the list of filters until there are none left, or we reach the search limit
    while artists.count() < limit and len(filters) > 0:
        filtr = _generate_q(text, filters.pop(0))
        try:
            artists = artists | attach_new_artists(filtr)
        except Exception as e:
            print(e)
        artists = artists.distinct()
    
    return artists[:limit]


def search_playlists(text, *args, **kwargs):
    pass

