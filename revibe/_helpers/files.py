from django.core.files.images import get_image_dimensions

import os

from content.models import Artist, Album, Image, Track

# -----------------------------------------------------------------------------

def add_image_to_obj(obj, img, *args, **kwargs):
    """
    """
    # skip everything if there is no image
    if img == None:
        return None

    # find out of the object is an artist or an album
    # then add the artist or the album to the objects
    objs = {}
    if isinstance(obj, Artist):
        objs['artist'] = obj
    elif isinstance(obj, Album):
        objs['album'] = obj

    if type(img) == str:
        image_obj = Image.objects.create(reference=img, is_original=True, height=1, width=1, **objs)
    elif type(img) == dict:
        image_obj = Image.objects.create(reference=img['image'], is_original=True, height=image['height'], width=image['width'], **objs)
    else: # image is the file
        image_obj = Image.objects.create(file=img, is_original=True, height=1, width=1, **objs)
        width, height = get_image_dimensions(image_obj.file.file)
        image_obj.width = width
        image_obj.height = height
        image_obj.save()

    return image_obj


def add_track_to_song(obj, track, *args, **kwargs):
    """
    """
    # skip everyting if there is no Track
    if track == None:
        return None

    objs = {
        "song": obj
    }

    if type(track) == str:
        track_obj = Track.objects.create(reference=track, is_original=True, **objs)
    elif type(track) == dict:
        track_obj = Track.objects.create(reference=track['track'], is_original=True, **objs)
    else:
        track_obj = Track.objects.create(file=track, is_original=True, **objs)
    
    track_obj.save()
    return track_obj
