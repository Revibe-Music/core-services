"""
Created: 04 June 2020
Author: Jordan Prechac
"""

import datetime

from accounts.models import CustomUser
from accounts.referrals.exceptions import ReferralException
from accounts.referrals.models import Point, PointCategory, Referral
from notifications.tasks import send_notification

# -----------------------------------------------------------------------------


def assign_points(referral_id, category, time_done: datetime.datetime = None):
    """
    # TODO: description of function


    Steps:
    1. get the Referral object
    2. Get the category referrenced
        a. Raise error if the Category is inactive
    3. Ensure the referrer has not received points for this category before,
        unless this is a repeating category
    4. Check expiration of event (either with datetime.now or 'time_done' param)
    5. TODO: Check for special point events and promotions
    6. Assign points
    7. Notify user that points were assigned (user Notifier)
    """
    # step 1
    referral = Referral.objects.get(id=referral_id)
    referrer = referral.referrer
    referree = referral.referree

    # step 2
    cat_name = " ".join([ word.capitalize() for word in category.split("_") ])
    try:
        category = PointCategory.objects.get(name__iexact=cat_name)
    except Category.DoesNotExist:
        raise ReferralException(f"Category with name '{cat_name}' does not exist")
    # step 2a
    if not category.active:
        raise ReferralException("Points are not currently being assigned for this activity")

    # step 3
    users_points = Point.objects.filter(referral=referral, category=category)
    if users_points.count() > 0 and (not category.repeating):
        raise ReferralException("This user has already been rewarded for this activity")

    # step 4
    if time_done and bool(category.expiration_interval):

        expire_date = referree.date_registered if referree.date_registered else referree.date_joined + datetime.timedelta(**{category.expiration_interval: category.expiration_number_of_periods})
        if time_done > expire_date:
            return 

    # step 5

    # step 6
    new_point = Point.objects.create(referral=referral, category=category, points=category.points)

    # step 7
    extra_configs = {"points": category.points}
    send_notification.s(
        referree.id, trigger="referral-points-assigned",
        force=True, medium='email', check_first=True, extra_configs=extra_configs
    ).delay()

    send_notification.s(
        referrer.id, trigger="referral-points-assigned-inverse",
        force=True, medium='email', check_first=True, extra_configs=extra_configs
    ).delay()




