"""
Created: 15 June 2020
"""

from .base import BranchDeepLinkingAPICreate

# -----------------------------------------------------------------------------


def song_link_from_template(song, template):

    link_data = {}

    # add link meta/tracking info
    link_data['channel'] = template.get_branch_channel()
    link_data['feature'] = template.medium.lower()
    link_data['campaign'] = template.get_branch_campaign()
    link_data['tags'] = template.tags_to_list()

    # add the link core fields
    data = {
        "$canonical_identifier": song.canonical_identifier,
        "$og_title": song.title,
        "$og_description": "Song - Revibe Music",
    }

    # if the template has tags 
    tags = template.tags_to_list()
    if tags != None: link_data['tags'] = tags

    # add the core data to the link data
    link_data['data'] = data

    branch = BranchDeepLinkingAPICreate(body=link_data)
    url = branch.send()

    if isinstance(url, str): return url
    raise Exception(f"Bad response: {url}")


