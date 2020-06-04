"""
"""

from celery import shared_task

from .utils.models.point import assign_points
from .utils.models.referral import get_referral

# -----------------------------------------------------------------------------

@shared_task
def add_referral_points(referred_user, category, time):
    referral = get_referral(referred_user)
    if not referral:
        return

    referral_id = referral.id

    assign_points(referral_id, category, time)


