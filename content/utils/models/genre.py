"""
Created: 22 Apr. 2020
Author: Jordan Prechac
"""

from content.models import Genre
from content.utils.types import _validate_list

# -----------------------------------------------------------------------------


def add_genres_to_object(genres, obj, *args, **kwargs):
    genres = _validate_list(genres)

    genre_objects = [Genre.objects.get_or_create(x) for x in genres]
    obj.genres.add(*genre_objects)

    return True

def remove_genres_from_object(genres, obj, *args, **kwargs):
    genres = _validate_list(genres)

    genre_objects = [Genre.objects.get_or_create(x) for x in genres]
    obj.genres.remove(*genre_objects)

    return True

def set_genres_on_object(genres, obj, *args, **kwargs):
    genres = _validate_list(genres)

    genre_objects = [Genre.objects.get_or_create(x) for x in genres]
    obj.genres.set(*genre_objects)
