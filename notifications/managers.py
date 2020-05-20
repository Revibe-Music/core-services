"""
Created: 08 May 2020
Author: Jordan Prechac
"""

from django.db import models


# -----------------------------------------------------------------------------

class EventManager(models.Manager):
    pass

class ActiveEventManager(EventManager):
    def get_queryset(self):
        return super().get_queryset().filter(active=True)


# external events
class ExternalEventManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(type='external')

    def create(self, **kwargs):
        kwargs.update({'type': 'external'})
        return super().create(**kwargs)


# temporal events
class TemporalEventManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(type='temporal')
    
    def create(self, **kwargs):
        kwargs.update({'type': 'temporal'})
        return super().create(**kwargs)


