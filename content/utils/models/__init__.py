"""
Created: 18 Mar. 2020
Author: Jordan Prechac
"""

from .tag import get_tag, add_tag_to_album, remove_tag_from_album, add_tag_to_song, remove_tag_from_song

# -----------------------------------------------------------------------------

__all__ = [
    # tag
    get_tag, add_tag_to_song, remove_tag_from_song, add_tag_to_album, remove_tag_from_album
]
