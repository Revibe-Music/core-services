"""
"""

from django.db import models

# -----------------------------------------------------------------------------


class PointManager(models.Manager):
    def get_user_points(self, user):
        return self.get_queryset().filter(
            models.Q(referral__referrer=user) | models.Q(user=user)
        )



