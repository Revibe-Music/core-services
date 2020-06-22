"""
author: Jordan Prechac
created: 23 Jan, 2020
"""

from django.db import connection
from django.conf import settings
from django.core.files.base import ContentFile
from django.core.files.images import get_image_dimensions

import gc
from io import BytesIO, StringIO
import boto3
import os
from PIL import Image as PILImage
from pydub import AudioSegment
import threading

from logging import getLogger
logger = getLogger(__name__)

from revibe.utils.aws.s3 import delete_s3_object
from revibe._errors import network

from content.models import Artist, Album, Image, Track
from content.tasks import convert_track_task

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
    reprocess = kwargs.pop('reprocess', False)
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

            if reprocess:
                if not item.is_original:
                    item.delete()
            else:
                item.delete()

    def process_image(image_obj):
        width, height = get_image_dimensions(image_obj.file.file)
        image_obj.width = width
        image_obj.height = height
        image_obj.save()

        # post processing, creating duplicates, etc...
        # create new thread...
        t = threading.Thread(target=resize_image_async, args=[image_obj])
        t.setDaemon(True)
        t.start()

        return image_obj

    # create the object
    if type(img) == str:
        image_obj = Image.objects.create(reference=img, is_original=True, height=1, width=1, **objs)
    elif type(img) == dict:
        image_obj = Image.objects.create(reference=img['image'], is_original=True, height=image['height'], width=image['width'], **objs)
    else: # image is the file
        if reprocess:
            image_obj = Image.objects.filter(**{f"{t}": obj, 'is_original': True}).first()
        else:
            image_obj = Image.objects.create(file=img, is_original=True, height=1, width=1, **objs) # image is stored in S3
        image_obj = process_image(image_obj)

    return image_obj


def resize_image_async(obj, *args, **kwargs):
    """
    takes the image from the django object and creates new images of the sizes needed
    """
    # get the string version of the object class, lowercase. 
    t = obj.obj.__class__.__name__.lower()

    img = obj.file
    sizes = [ # width x height
        (64,64),
        (300,300),
        (600,600),
    ]
    ext = obj.file.name.split('.')[-1].lower()
    ext = "jpeg" if ext == 'jpg' else ext

    # open the file as a PIL Image object and 
    # crop original to a square for resizing
    original_image = square_image(PILImage.open(obj.file))

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

        # free memory
        del content_file
        del f
        del s
        gc.collect()

    del original_image
    gc.collect()

    connection.close()


def square_image(image):
    """
    Squares a PIL Image
    """
    width, height = image.size
    if width == height:
        return image
    
    size = min(width, height)

    extra_width = width - size
    extra_height = height - size

    # define the box
    left = extra_width / 2
    right = left + size
    upper = extra_height / 2
    lower = upper + size

    return image.crop((left, upper, right, lower))


def add_track_to_song(obj, track, *args, **kwargs):
    """
    """
    editing = kwargs.pop('edit', False)
    admin_edit = kwargs.pop('admin_edit', False)

    # skip everyting if there is no Track
    if (not track) and (not admin_edit):
        return None

    objs = {
        "song": obj
    }

    # delete the old processed files, if there are any
    if editing or admin_edit:
        # delete all the existing tracks
        # unless admin editing, then only delete processed tracks
        tracks = obj.tracks.all() if editing else obj.tracks.filter(is_original=False)
        for t in tracks:
            t.delete()

    if isinstance(track, str):
        track_obj = Track.objects.create(reference=track, is_original=True, **objs)
    elif isinstance(track, dict):
        track_obj = Track.objects.create(reference=track['track'], is_original=True, **objs)
    else: # it's a file
        if not admin_edit:
            track_obj = Track.objects.create(file=track, is_original=True, **objs)
        else:
            # get the original track. If one doesn't exist, raise an error
            try:
                track_obj = Track.objects.get(is_original=True, song=obj)
            except Track.DoesNotExist:
                raise network.ExpectationFailedError("The song does not have an original track")
        # convert_audio_file(track_obj)

        # create other audio files in a thread
        # t = threading.Thread(target=convert_audio_file, args=[track_obj])
        # t.setDaemon(True)
        # t.start()
        convert_track_task \
            .s(track_obj.song.id) \
            .set(countdown=10) \
            .delay()

    track_obj.save()
    return track_obj


# def convert_audio_file(obj, *args, **kwargs):
#     """
#     Takes an input audio file and converts it to 3 different quality AAc files.
#     """
#     # pass
#     print("new thread!")
#     if not obj.file:
#         return None

#     ext = obj.file.name.split('.')[-1]
#     print("File extension: ", ext)
#     new_formats = [
#         {
#             "format": "mp4",
#             "encoding": "aac",
#             "bitrate": "96k",
#             "filename": "low",
#         },
#         {
#             "format": "mp4",
#             "encoding": "aac",
#             "bitrate": "128k",
#             "filename": "medium",
#         },
#         {
#             "format": "mp4",
#             "encoding": "aac",
#             "bitrate":"256k",
#             "filename": "high",
#         },
#     ]

#     byte_data = obj.file.read()
#     byte_format = BytesIO(byte_data)

#     segment = AudioSegment.from_file(file=byte_format, format=ext)
#     logger.info("Created audio segment")
#     logger.debug(segment)

#     # for f in formats:
#     for f in new_formats:
#         channels = f.get('channels', 2)
#         output = BytesIO()
#         segment.export(output, format=f['format'], codec=f['encoding'], bitrate=f['bitrate'], parameters=["-ac", str(channels)])

#         value = output.getvalue()
#         file_name = f"{f['filename']}.{f['format']}"

#         track = Track.objects.create(is_original=False, song=obj.song)
#         track.file.save(file_name, ContentFile(value))
#         track.save()
#         logger.info(f"File {file_name} has been created.")

#         del value
#         gc.collect()

#     del segment
#     gc.collect()

#     connection.close()


