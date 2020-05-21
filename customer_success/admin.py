from django.contrib import admin

from .models import *
from .utils.admin.inlines import PathwayActionInline

# -----------------------------------------------------------------------------

@admin.register(Pathway)
class PathwayAdmin(admin.ModelAdmin):
    fieldsets = (
        (None, {
            "fields": ('name', 'type', 'default',),
            "classes": ('extrapretty', 'wide',),
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
        ("Extras", {
            "fields": ('active', 'description', 'date_created', 'last_changed',),
            "classes": ('extrapretty', 'wide', 'collapse', 'in',),
        })
    )
    readonly_fields = ('date_created', 'last_changed',)

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
            "fields": ('pathway', 'action', 'ranking',),
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
    pass


