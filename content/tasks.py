"""
"""

from celery import shared_task

# from revibe.utils.mail import error_email

from administration.models import ContactForm

from .utils.models.track import convert_track

# -----------------------------------------------------------------------------

@shared_task
def convert_track_task(song_id, *args, **kwargs):
    try:
        worked = convert_track(song_id, *args, **kwargs)
        if not bool(worked):
            raise ValueError("Bad stuff happened in there...")
    except Exception as e:
        # error_email(
        #     "jordanprechac@revibe.tech",
        #     "celery.task.convert_track_task",
        #     e,
        #     False
        # )

        ContactForm.objects.create(subject="Failed Celery Song Processing", message=f"Song id: {song_id}")

        raise e


