from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from .models import *
from .utils.admin.inlines import PathwayActionInline, PathUsersInline

# -----------------------------------------------------------------------------

@admin.register(Pathway)
class PathwayAdmin(admin.ModelAdmin):
    fieldsets = (
        (None, {
            "fields": ('name', 'type', 'default',),
            "classes": ('extrapretty', 'wide',),
        }),
        ("Progression", {
            "fields": ('beginner_quota', 'intermediate_quota', 'advanced_quota', 'special_quota', 'other_quota'),
            "classes": ('extrapretty', 'wide',),
            "description": _("The percentage of actions a user must complete in each rank to progress to the next rank.")
        }),
        ("Extras", {
            "fields": ('description', 'date_created', 'last_changed',),
            "classes": ('extrapretty', 'wide', 'collapse', 'in',),
        })
    )
    readonly_fields = ('date_created', 'last_changed',)

    list_display = (
        'name',
        'type',
        'default',
    )
    list_filter = (
        ('default', admin.BooleanFieldListFilter),
        'type',
    )

    inlines = [
        PathwayActionInline,
        PathUsersInline,
    ]

    search_fields = [
        'name'
    ]


@admin.register(Action)
class ActionAdmin(admin.ModelAdmin):
    fieldsets = (
        (None, {
            "fields": ('name',),
            "classes": ('extrapretty', 'wide',),
        }),
        ("Notifications", {
            "fields": ('event', 'extra_events', 'interval_period', 'number_of_period',),
            "classes": ('extrapretty', 'wide',),
        }),
        ("Recurrence", {
            "fields": ('recurring', 'recur_interval_period', 'recur_number_of_periods',),
            "classes": ('extrapretty', 'wide',),
            "description": Action.RECURRENCE_DESCRIPTION,
        }),
        ("Verification", {
            "fields": ('required_request_body_kwargs', 'required_request_params_kwargs', 'required_response_body_kwargs',),
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
        'event',
        'active',
    )
    list_filter = (
        ('event', admin.RelatedOnlyFieldListFilter),
        ('active', admin.BooleanFieldListFilter),
    )

    inlines = [
        PathwayActionInline,
    ]

    search_fields = [
        'name',
        # 'pathways__name',
        'event__name',
    ]


@admin.register(PathwayAction)
class PathwayActionAdmin(admin.ModelAdmin):
    fieldsets = (
        (None, {
            "fields": ('pathway', 'action', 'ranking', 'allow_recurrence',),
            "classes": ('extrapretty', 'wide',),
        }),
        ("Extras", {
            "fields": ('active', 'description', 'date_created', 'last_changed',),
            "classes": ('extrapretty', 'wide', 'collapse', 'in')
        })
    )
    readonly_fields = ('date_created', 'last_changed',)

    list_display = (
        'pathway', 
        'action',
        'ranking',
        'active',
    )
    list_filter = (
        ('pathway', admin.RelatedOnlyFieldListFilter),
        'ranking',
        ('active', admin.BooleanFieldListFilter),
    )

    search_fields = [
        'pathway__name',
        'action__name',
    ]


@admin.register(ActionTaken)
class ActionTakenAdmin(admin.ModelAdmin):
    readonly_fields = ('timestamp',)

    list_display = (
        'action',
        'user',
        'notification',
    )
    list_filter = (
        ('timestamp', admin.DateFieldListFilter),
    )


