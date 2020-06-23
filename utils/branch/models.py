"""
Created: 15 June 2020
"""

from .base import BranchDeepLinkingAPICreate
from .exceptions import BranchException

# -----------------------------------------------------------------------------

def _link_from_template(data, template):
    link_data = {}

    # add link meta/tracking info
    link_data['channel'] = template.get_branch_channel()
    link_data['feature'] = template.medium.lower()
    link_data['campaign'] = template.get_branch_campaign()
    link_data['tags'] = template.tags_to_list()

    # if the template has tags, add them
    tags = template.tags_to_list()
    if tags != None: link_data['tags'] = tags

    link_data['data'] = data

    branch = BranchDeepLinkingAPICreate(body=link_data)
    url = branch.send()

    if isinstance(url, str): return url

    raise BranchException(f"Bad response: {url}")

def song_link_from_template(song, template):
    # add the link core fields
    data = {
        "$canonical_identifier": song.canonical_identifier,
        "$og_title": song.title,
        "$og_description": "Song - Revibe Music",
    }

    return _link_from_template(data, template)

def album_link_from_template(album, template):
    # add the link data core fields
    data = {
        "$canonical_identifier": album.canonical_identifier,
        "$og_title": album.name,
        "$og_description": "Album - Revibe Music",
    }

    return _link_from_template(data, template)

def artist_link_from_template(artist, template):
    # add the link data core fields
    data = {
        "$canonical_identifier": artist.canonical_identifier,
        "$og_title": artist.name,
        "$og_description": "Artist - Revibe Music",
    }

    return _link_from_template(data, template)

