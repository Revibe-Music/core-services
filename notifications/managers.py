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
