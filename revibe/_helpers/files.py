"""
author: Jordan Prechac
created: 23 Jan, 2020
"""

from django.conf import settings
from django.core.files.base import ContentFile
from django.core.files.images import get_image_dimensions

from io import BytesIO
import boto3
import os
from PIL import Image as PILImage
import threading

from content.models import Artist, Album, Image, Track

# -----------------------------------------------------------------------------

# multi-threading (for post-processing)
# https://stackoverflow.com/questions/17601698/can-django-do-multi-thread-works

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
        t = 'artist'
    elif isinstance(obj, Album):
        objs['album'] = obj
        t = 'album'

    # delete old objects in S3 if editing:
    editing = kwargs.pop('edit', False)
    if editing:
        prefix = f"images/{obj.__class__.__name__}/{str(obj.uri)}/"

        # delete the old objects from the database and S3
        if settings.USE_S3:
            s3 = boto3.resource('s3')
        image_mngr = getattr(obj, f"{t}_image")
        images = image_mngr.all()
        for item in images:
            if item.file:
                if settings.USE_S3:
                    s3.Object(settings.AWS_STORAGE_BUCKET_NAME, item.file.name)#.delete()
                # else: # delete file locally... who cares...
            
            item.delete()
    
    # create the object
    if type(img) == str:
        image_obj = Image.objects.create(reference=img, is_original=True, height=1, width=1, **objs)
    elif type(img) == dict:
        image_obj = Image.objects.create(reference=img['image'], is_original=True, height=image['height'], width=image['width'], **objs)
    else: # image is the file
        image_obj = Image.objects.create(file=img, is_original=True, height=1, width=1, **objs) # image is stored in S3
        # everything after is pulling back that file from S3
        width, height = get_image_dimensions(image_obj.file.file)
        image_obj.width = width
        image_obj.height = height
        image_obj.save()

        # post processing, creating duplicates, etc...
        # create new thread...
        t = threading.Thread(target=resize_image, args=[image_obj])
        t.setDaemon(True)
        t.start()

    return image_obj


def add_track_to_song(obj, track, *args, **kwargs):
    """
    """
    # skip everyting if there is no Track
    if not track:
        return None

    objs = {
        "song": obj
    }

    editing = kwargs.pop('edit', False)
    if editing:
        prefix = f"audio/songs/{str(obj.uri)}/"
        tracks = obj.tracks.all()
        if settings.USE_S3:
            s3 = boto3.resource('s3')
        for t in tracks:
            if settings.USE_S3:
                s3.Object(settings.AWS_STORAGE_BUCKET_NAME, t.file.name).delete()
            t.delete()

    if type(track) == str:
        track_obj = Track.objects.create(reference=track, is_original=True, **objs)
    elif type(track) == dict:
        track_obj = Track.objects.create(reference=track['track'], is_original=True, **objs)
    else:
        track_obj = Track.objects.create(file=track, is_original=True, **objs)
    
    track_obj.save()
    return track_obj


def resize_image(obj, *args, **kwargs):
    """
    takes the image from the django object and creates new images of the sizes needed
    """
    # get the string version of the object class, lowercase. 
    t = obj.obj.__class__.__name__.lower()

    img = obj.file
    sizes = [ # width x height
        (50,50),
        (100,100),
        (200,200),
    ]
    ext = obj.file.name.split('.')[-1].lower()
    ext = "jpeg" if ext == 'jpg' else ext

    original_image = PILImage.open(obj.file)

    # generate a new image for each required dimension
    for dimension in sizes:
        f = BytesIO()
        original_image.save(f, format=ext)
        s = f.getvalue()

        # resize file
        pil_image_obj = PILImage.open(BytesIO(s))
        pil_image_obj = pil_image_obj.resize(dimension)

        # resave variables with newly resized image
        f = BytesIO()
        pil_image_obj.save(f, format=ext)
        s = f.getvalue()

        content_file = ContentFile(s)

        file_name = f"{dimension[0]}x{dimension[1]}.{ext}"

        image_obj = Image.objects.create(is_original=False, height=dimension[1], width=dimension[0], **{t:obj.obj})
        image_obj.file.save(file_name, content_file)
        image_obj.save()

