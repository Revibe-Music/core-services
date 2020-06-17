"""
The Branch module handles all the interactactions between our servers and the Branch API.

We use Branch to generate links to our content in Revibe Music and Revibe Artists 
that can be tracked, providing valuable data for our marketing team. 

Created: 09 June 2020
"""

from .models import song_link_from_template, album_link_from_template, artist_link_from_template

# -----------------------------------------------------------------------------

__all__ = [
    song_link_from_template, album_link_from_template, artist_link_from_template
]
