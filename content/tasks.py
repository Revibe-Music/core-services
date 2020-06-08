"""
"""

from celery import shared_task

from .utils.models.track import convert_track

# -----------------------------------------------------------------------------

@shared_task
def convert_track_task(song_id, *args, **kwargs):
    return convert_track(song_id, *args, **kwargs)


