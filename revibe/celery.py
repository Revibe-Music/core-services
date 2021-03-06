from __future__ import absolute_import, unicode_literals

import os

import django
from django.conf import settings
from celery import Celery


# set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'revibe.settings.dev')

# django.setup()

app = Celery('revibe')

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
# - namespace='CELERY' means all celery-related configuration keys
#   should have a `CELERY_` prefix.
app.config_from_object('django.conf:settings', namespace="CELERY") # only for celery >= 4.0
# app.config_from_object('django.conf:settings') # for celery < 4.0

# Load task modules from all registered Django app configs.
app.autodiscover_tasks() # default thing
# app.autodiscover_tasks(settings.INSTALLED_APPS) # use this to discover all tasks. May be necessary in the future

# based on this thred: https://stackoverflow.com/questions/47043693/celery-4-not-auto-discovering-tasks
# app.config_from_object(settings, namespace='CELERY')
# app.autodiscover_tasks(lambda: settings.INSTALLED_APPS, force=True)


@app.task(bind=True)
def debug_task(self):
    print('Request: {0!r}'.format(self.request))