from django.apps import apps
from django.conf import settings
from django.core.files.base import ContentFile

import gc
from io import BytesIO
import os
from pydub import AudioSegment

# -----------------------------------------------------------------------------



def process_audio_file(song):
    Song = apps.get_model('content', 'Song')
    Track = apps.get_model('content', 'Track')

    # if the 'song' parameter isn't a Song model object,
    # assume it's an ID and try to get a Song from it
    if not isinstance(song, Song):
        song = Song.objects.get(id=song)

    # get the original Track from the song
    # if there isn't one, raise an error
    tracks = song.tracks.filter(is_original=True)
    if not tracks.exists():
        raise ValueError("No valid 'Track' objects could be found in this Song")
    track = tracks.first()

    if not track.file:
        raise ValueError("The Track object does not have a file")

    # get the file extension
    ext = track.file.name.split('.')[-1]

    # audio formats to convert to are defined in settings
    new_formats = settings.AUDIO_FILE_OUTPUT_FORMATS

    # convert the audio file to a Byte format
    byte_data = track.file.read()
    byte_format = BytesIO(byte_data)

    # create an AudioSegment from that Byte data
    segment = AudioSegment.from_file(file=byte_format, format=ext)

    for formt in new_formats:
        channels = formt.get('channels', 2)
        output = BytesIO()

        # export the data into a new Byte object
        segment.export(output, format=formt['format'], codec=formt['encoding'], bitrate=formt['bitrate'], parameters=["-ac", str(channels)])
        value = output.getvalue()

        file_name = f"{formt['filename']}.{formt['format']}"

        # create a new Track object from the new data
        track = Track.objects.create(is_original=False, song=song)
        # convert the Byte data into a new ContentFile
        track.file.save(file_name, ContentFile(value))
        track.save()

        del value
        gc.collect()
    
    del segment
    gc.collect()

    return True
        


