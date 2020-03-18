"""
Created: 18 Mar. 2020
Author: Jordan Prechac
"""

from .placeholder_contribution import create_permananent_contribs, create_placeholder
from .tag import get_tag, add_tag_to_album, remove_tag_from_album, add_tag_to_song, remove_tag_from_song

# -----------------------------------------------------------------------------

__all__ = [
    # placeholder contribution
    create_permananent_contribs, create_placeholder,

    # tag
    get_tag, add_tag_to_song, remove_tag_from_song, add_tag_to_album, remove_tag_from_album
]
