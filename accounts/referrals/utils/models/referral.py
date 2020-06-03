"""
"""

from revibe.utils.params import get_url_param

from accounts.referrals.exceptions import ReferralException
from accounts.referrals.models import Referral

# -----------------------------------------------------------------------------


def attach_referral(referrer, referree, ip_address=None, *args, **kwargs):
    # check that the referred user (referree) has not already been referred
    check = Referral.objects.filter(referree=referree).count()
    if check > 0:
        raise ReferralException("This user has already been referred")

    # check that the referred user has registered in the allowed time
    # TODO: implement

    # do IP address validation
    # TODO: implement

    # create a Referral object
    referral = Referral.objects.create(referrer=referrer, referree=referree, referree_ip_address=ip_address)

    # do a points thing with the referral

    return referral

