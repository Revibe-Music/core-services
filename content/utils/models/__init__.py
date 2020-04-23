"""
Created: 18 Mar. 2020
Author: Jordan Prechac
"""

from .placeholder_contribution import create_permananent_contribs, create_placeholder
from .tag import get_tag, add_tag_to_album, remove_tag_from_album, add_tag_to_song, remove_tag_from_song
from .genre import add_genres_to_object, remove_genres_from_object, set_genres_on_object

# -----------------------------------------------------------------------------

__all__ = [
    # placeholder contribution
    create_permananent_contribs, create_placeholder,

    # tag
    get_tag, add_tag_to_song, remove_tag_from_song, add_tag_to_album, remove_tag_from_album,

    # genre
    add_genres_to_object, remove_genres_from_object, set_genres_on_object,
]
