"""
"""

from celery import shared_task

from revibe.utils.mail import error_email

from .utils.models.track import convert_track

# -----------------------------------------------------------------------------

@shared_task
def convert_track_task(song_id, *args, **kwargs):
    try:
        return convert_track(song_id, *args, **kwargs)
    except Exception as e:
        error_email(
            "jordanprechac@revibe.tech",
            "celery.task.convert_track_task",
            e,
            False
        )

        raise e


