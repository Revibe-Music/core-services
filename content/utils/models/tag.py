"""
Created: 17 Feb. 2020
Author: Jordan Prechac
"""

from content.models import Album, Song, Tag
from content.utils.types import _validate_list

# -----------------------------------------------------------------------------

def get_tag(text, *args, **kwargs):
    """
    Retrieves a tag, or creates one and returns that
    """
    text = text.lower()
    try:
        tag = Tag.objects.get(text=text)
    except Tag.DoesNotExist:
        tag = Tag.objects.create(text=text)
    
    return tag


def add_tag_to_song(tags, song, raise_exception: bool=False, *args, **kwargs):
    """
    Add tags to a song
    """
    # enforce that the 'tags' are a list
    tags = _validate_list(tags)

    # get the song, if the sent data isn't already a Song object
    if type(song) != Song:
        song = Song.objects.get(id=song)

    # get a list of all the tags
    tag_objects = [get_tag(x) for x in tags]
    song.tags.add(*tag_objects)

    return True


def remove_tag_from_song(tags, song, *args, **kwargs):
    """
    Remove tags from a song
    """
    # enforce that the 'tags' are a list
    tags = _validate_list(tags)

    if type(song) != Song:
        song = Song.objects.get(id=song)
    
    # get a list of all the tags
    tag_objects = [get_tag(x) for x in tags]
    song.tags.remove(*tag_objects)
    
    return True


def add_tag_to_album(tags, album, raise_exception: bool=False, *args, **kwargs):
    """
    Add tags to an album
    """
    # enforce that the 'tags' are a list
    tags = _validate_list(tags)

    # get the album, if the sent data isn't already an album object
    if type(album) != Album:
        album = Album.objects.get(id=album)
    
    # get a list of all the tags
    tag_objects = [get_tag(x) for x in tags]
    album.tags.add(*tag_objects)

    return True


def remove_tag_from_album(tags, album, *args, **kwargs):
    """
    Remove tags from an album
    """
    # enforce that the 'tags' are a list
    tags = _validate_list(tags)

    if type(album) != Album:
        album = Album.objects.get(id=album)
    
    tag_objects = [get_tag(x) for x in tags]
    album.tags.remove(*tag_objects)

    return True

