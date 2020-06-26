"""
"""

from django.core.files.base import ContentFile

import gc
from io import BytesIO, StringIO
import boto3
import os
from pydub import AudioSegment

from revibe.exceptions import api

from content.models import Song, Track

# -----------------------------------------------------------------------------


def convert_track(song_id, *args, **kwargs):
    song = Song.objects.get(id=song_id)

    tracks = song.tracks.filter(is_original=True)
    if not tracks.exists():
        raise api.NotFoundError("Could not identify a valid Track object")

    track = tracks.first()

    # get the necessary file info
    if not track.file:
        return None
    ext = track.file.name.split('.')[-1]
    print("File extension: ", ext)

    # define file formats
    new_formats = [
        {
            "format": "mp4",
            "encoding": "aac",
            "bitrate": "96k",
            "filename": "low",
        },
        {
            "format": "mp4",
            "encoding": "aac",
            "bitrate": "128k",
            "filename": "medium",
        },
        {
            "format": "mp4",
            "encoding": "aac",
            "bitrate":"256k",
            "filename": "high",
        },
    ]

    byte_data = track.file.read()
    byte_format = BytesIO(byte_data)

    segment = AudioSegment.from_file(file=byte_format, format=ext)

    for f in new_formats:
        channels = f.get('channels', 2)
        output = BytesIO()
        segment.export(output, format=f['format'], codec=f['encoding'], bitrate=f['bitrate'], parameters=["-ac", str(channels)])

        value = output.getvalue()
        file_name = f"{f['filename']}.{f['format']}"

        track = Track.objects.create(is_original=False, song=song)
        track.file.save(file_name, ContentFile(value))
        track.save()

        del value
        gc.collect()

    del segment
    gc.collect()

    return True


