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


@admin.register(PointCategory)
class PointCategoryAdmin(admin.ModelAdmin):
    fieldsets = (
        (None, {
            "fields": ('name', 'points',),
            "classes": ('extrapretty', 'wide',),
        }),
        ("Configuration", {
            "fields": ('repeating', 'expiration_interval', 'expiration_number_of_periods',),
            "classes": ('extrapretty', 'wide',),
        }),
        ("Extras", {
            "fields": ('active', 'description', 'date_created', 'last_changed', 'id',),
            "classes": ('extrapretty', 'wide', 'collapse', 'in',),
        })
    )
    readonly_fields = (
        'id',
        'date_created', 'last_changed',
    )

    list_display = (
        'name',
        'points',
        'active',
    )
    list_filter = (
        ('active', admin.BooleanFieldListFilter),
    )

    search_fields = (
        'name',
        'description',
    )


@admin.register(Point)
class PointAdmin(admin.ModelAdmin):
    fieldsets = (
        (None, {
            "fields": ('user', 'referral', 'category', 'points',),
            "classes": ('extrapretty', 'wide',),
        }),
        ("Extras", {
            "fields": ('timestamp', 'id',),
            "classes": ('extrapretty', 'wide', 'collapse', 'in',),
        }),
    )
    readonly_fields = (
        'id',
        'timestamp',
    )

    list_display = (
        '_user',
        'points',
        'category',
    )
    list_filter = (
        ('timestamp', admin.DateFieldListFilter),
    )

    def _user(self, obj):
        if obj.referral:
            return obj.referral.referrer
    _user.short_description = "referring user"



