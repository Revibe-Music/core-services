"""
Created: 03 June 2020
Author: Jordan Prechac
"""

from django.contrib import admin

from .models import *

# -----------------------------------------------------------------------------


@admin.register(Referral)
class ReferralAdmin(admin.ModelAdmin):
    readonly_fields = ('id', 'timestamp',)

    list_display = (
        'id',
        '_link_to_referrer',
        '_link_to_referree',
    )
    list_filter = (
        ('timestamp', admin.DateFieldListFilter),
    )


    def _link_to_referrer(self, obj):
        if getattr(obj, 'referrer', None):
            return obj.referrer._link_to_self()
    _link_to_referrer.short_description = "sent"
    _link_to_referrer.admin_order_field = "referrer"

    def _link_to_referree(self, obj):
        if getattr(obj, 'referree', None):
            return obj.referree._link_to_self()
    _link_to_referree.short_description = "referred"
    _link_to_referree.admin_order_field = "referree"


