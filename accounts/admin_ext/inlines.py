"""
Created: 22 May 2020
Author: Jordan Prechac
"""

from django.contrib import admin

from accounts.models import ArtistProfile
from accounts.referrals.models import Referral

# -----------------------------------------------------------------------------


class ArtistProfileInline(admin.StackedInline):
    model = ArtistProfile


class ReferralInline(admin.TabularInline):
    model = Referral
    fk_name = "referrer"


