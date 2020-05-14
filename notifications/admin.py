from django.contrib import admin

from .models import *

# -----------------------------------------------------------------------------

@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    # customize list display
    list_display = (
        'name',
        'trigger',
        'desired_action',
        'active',
    )
    list_filter = (
        'desired_action',
        ('active', admin.BooleanFieldListFilter),
    )

    # customize search
    search_fields = [
        'name',
        'trigger',
        'desired_action',
        'description',
    ]

    fieldsets = (
        (None, {
            'fields': ('name', 'trigger', 'desired_action'),
            'classes': ('extrapretty', 'wide'),
        }),
        ('Email', {
            'fields': ('sent_address',),
            'classes': ('extrapretty', 'wide', 'collapse', 'in'),
        }),
        ('Configuration', {
            'fields': ('active', 'description', 'date_created', 'last_changed', ),
            'classes': ('extrapretty', 'wide', 'collapse', 'in'),
        }),
    )
    readonly_fields = (
        'date_created', 'last_changed',
    )


@admin.register(NotificationTemplate)
class NotificationTemplateAdmin(admin.ModelAdmin):
    # customize list display
    list_display = (
        '__str__',
        'event',
    )
    list_filter = (
        ('event', admin.RelatedOnlyFieldListFilter),
        ('event__active', admin.BooleanFieldListFilter),
    )

    # customize search
    search_fields = [
        'event__name',
        'text_template',
        'event__trigger',
        'event__desired_action',
        'description',
        'event__description',
    ]

    fieldsets = (
        (None, {
            'fields': ('event', 'medium', 'body',),
            'classes': ('extrapretty', 'wide',),
        }),
        ('Email', {
            'fields': ('subject', ),
            'classes': ('extrapretty', 'wide', 'collapse', 'in'),
        }),
        ('Configuration', {
            'fields': ('active', 'description', 'date_created', 'last_changed',),
            'classes': ('extrapretty', 'wide', 'collapse', 'in'),
        }),
    )
    readonly_fields = (
        'date_created',
        'last_changed',
    )


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    # customize list display
    list_display = (
        'user',
        '_event_name',
        'seen',
        'action_taken',
    )
    list_filter = (
        ('date_created', admin.DateFieldListFilter),
        ('date_of_action', admin.DateFieldListFilter),
        ('user', admin.RelatedOnlyFieldListFilter),
        ('action_taken', admin.BooleanFieldListFilter),
        ('seen', admin.BooleanFieldListFilter),
        ('event_template__event', admin.RelatedOnlyFieldListFilter),
    )

    def _event_name(self, obj):
        try:
            return obj.event_template.event.name
        except Exception:
            return None
    _event_name.short_description = 'event'
    _event_name.admin_order_field = 'event_template__event__name'

