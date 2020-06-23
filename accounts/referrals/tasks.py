"""
"""

from celery import shared_task

# from accounts.models import CustomUser
from django.apps import apps

from accounts.referrals.utils.models.point import assign_points
from accounts.referrals.utils.models.referral import get_referral

# -----------------------------------------------------------------------------

@shared_task
def add_referral_points(referred_user_id, category, time):
    CustomUser = apps.get_model('accounts', 'CustomUser')

    referred_user = CustomUser.objects.get(id=referred_user_id)
    referral = get_referral(referred_user)
    if not referral:
        return

    referral_id = referral.id

    assign_points(referral_id, category, time)


