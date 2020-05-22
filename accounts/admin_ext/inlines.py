"""
Created: 22 May 2020
Author: Jordan Prechac
"""

from django.contrib import admin

from accounts.models import ArtistProfile

# -----------------------------------------------------------------------------


class ArtistProfileInline(admin.StackedInline):
    model = ArtistProfile

