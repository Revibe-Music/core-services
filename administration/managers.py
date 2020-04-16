from django.db import models # models.Manager
from django.db.models import F, Q

import datetime

# -----------------------------------------------------------------------------

class AlertDisplayManager(models.Manager):
    def get_queryset(self):
        q_filter = Q(
            enabled=True,
            start_date__lte=datetime.datetime.now(),
            end_date__gte=datetime.datetime.now()
        )
        return super().get_queryset().filter(q_filter)


class BlogDisplayManager(models.Manager):
    def get_queryset(self):
        q_filter = Q(
            publish_date__lte=datetime.date.today()
        )
        return super().get_queryset().filter(q_filter)


class YouTubeKeyManager(models.Manager):
    def get_queryset(self):
        points_per_user = models.ExpressionWrapper(
            F('point_budget') / F('number_of_users'),
            output_field = models.DecimalField()
        )
        annotation = {"points_per_user": points_per_user}
        return super().get_queryset().annotate(**annotation)
