"""
Created: 17 Feb. 2020
Author: Jordan Prechac
"""

from content.models import Song, Tag


# -----------------------------------------------------------------------------

def get_tag(text, *args, **kwargs):
    """
    Retrieves a tag, or creates one and returns that
    """
    try:
        tag = Tag.objects.get(text=text)
    except Tag.DoesNotExist:
        tag = Tag.objects.create(text=text)
    
    return tag


def add_tag_to_song(tags, song, *args, **kwargs):
    """
    Add tags to a song
    """
    # get the song, if the sent data isn't already a Song object
    if type(song) != Song:
        song = Song.objects.get(id=song)

    # get a list of all the tags
    tag_objects = [get_tag(x) for x in tags]
    for t in tag_objects:
        song.tags.add(t)

    return True

def remove_tag_from_song(tags, song, *args, **kwargs):
    """
    Remove tags from a song
    """
    if type(song) != Song:
        song = Song.objects.get(id=song)
    
    # get a list of all the tags
    tag_objects = [get_tag(x) for x in tags]
    for t in tag_objects:
        song.tags.remove(t)
    
    return True

