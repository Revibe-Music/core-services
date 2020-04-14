"""
Created: 14 Apr. 2020
Author: Jordan Prechac
"""

from django.db import models
from django.db.models import Q

# -----------------------------------------------------------------------------

# Stream extra metrics 
class StreamMetricsManager(models.Manager):
    def get_queryset(self):
        stream_percentage_calc = models.ExpressionWrapper(models.F('stream_duration') / models.F('song__duration'), output_field=models.DecimalField())
        return super().get_queryset().annotate(
            stream_percentage=stream_percentage_calc
        )
