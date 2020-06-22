"""
"""

from __future__ import absolute_import, unicode_literals

from celery import shared_task

from django.apps import apps
Song = apps.get_model('content', 'Song')

from content.tasks.track_processing import process_audio_file

# -----------------------------------------------------------------------------

# @app.task(bind=True)
@shared_task
def convert_track_task(*args, **kwargs):
    process_audio_file(*args, **kwargs)

