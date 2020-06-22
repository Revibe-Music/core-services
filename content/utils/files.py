from django.apps import apps
from django.core.exceptions import ObjectDoesNotExist
from django.core.files.base import ContentFile, File

from io import BytesIO, StringIO
import os
from pydub import AudioSegment
import threading

Song = apps.get_model('content', 'Song')
Track = apps.get_model('content', 'Track')
Variable = apps.get_model('administration', 'Variable')

def _start_processing(song: Song):
    """
    """
    from content.tasks import convert_track_task
    use_celery_processing = Variable.objects.retrieve('audio-processing-use-celery', False, output_type=bool)

    if use_celery_processing:
        convert_track_task.s(str(song.id)) \
            .set(countdown=10) \
            .delay()
    
    else:
        t = threading.Thread(target=convert_track_task, args=[song])
        t.setDaemon(True)
        t.start()


def add_track_to_song(song: Song, track: File=None, editing: bool=False, admin_edit: bool=False):
    # assert argument types
    if not isinstance(song, Song): raise TypeError("Parameter 'song' must be a Song object")
    if track and not isinstance(track, File): raise TypeError(f"Parameter 'track' must be a TemporaryUploadedFile object. Type: {type(track)}")

    # skip everything if there is no track
    if (not track) and (not admin_edit):
        raise ValueError("Must include a track object if not editing")

    if editing or admin_edit:
        # delete all existing tracks
        # if reprocessing from admin, only delete processed tracks
        tracks = song.tracks.all() if editing else song.tracks.filter(is_original=False)
        tracks.delete()

    if isinstance(track, str):
        new_track = Track.objects.create(reference=track, is_original=True, song=song)
        return new_track
    elif isinstance(track, dict):
        new_track = Track.objects.create(refernce=track['track'], is_original=True, song=song)
        return new_track
    else: # it's a file
        if not admin_edit:
            track_obj = Track.objects.create(file=track, is_original=True, song=song)
        else:
            # get the original track from the song
            track_obj = song.tracks.first()

            # raise an exception if there is no track
            if track_obj == None: raise ObjectDoesNotExist("Could not find a Track instance")

        _start_processing(song)

        return track




