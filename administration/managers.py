from django.core.exceptions import ObjectDoesNotExist
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


class ArtistOfTheWeekActiveManager(models.Manager):
    def get_queryset(self):
        q_filter = Q(
            active=True
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


class VariableManger(models.Manager):
    def retrieve(self, text, default, output_type=str):
        try:
            var = self.get(key=text)
            value = var.value
        except ObjectDoesNotExist:
            return default

        if output_type == bool:
            if value in ['False', 'false', 'f', 'F', '0']:
                return False
            elif value in ['True', 'true', 'T', 't', '1']:
                return True
            return default

        try:
            return output_type(value)
        except ValueError:
            return value


