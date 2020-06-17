"""
Created: 22 May 2020
Author: Jordan Prechac
"""

from django.contrib import admin

from accounts.models import ArtistProfile, Profile
from accounts.referrals.models import Referral

# -----------------------------------------------------------------------------


class ArtistProfileInline(admin.StackedInline):
    model = ArtistProfile


class ReferralInline(admin.TabularInline):
    model = Referral
    fk_name = "referrer"

    extra = 0


class ProfileInline(admin.StackedInline):
    model = Profile
    fk_name = "user"

    verbose_name = "profile"
    verbose_name_plural = verbose_name # this is a 1:1 field, so there is no need for a plural

