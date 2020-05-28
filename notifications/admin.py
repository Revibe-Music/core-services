from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from customer_success.utils.admin.inlines import ExternalEventActionInLine

from .models import *
from .utils.admin import actions

# -----------------------------------------------------------------------------

class EventAdmin(admin.ModelAdmin):
    # customize list display
    list_display = (
        'name',
        'trigger',
        'active',
    )
    list_filter = (
        'sent_address',
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
            'fields': ('name', 'trigger',),
            'classes': ('extrapretty', 'wide'),
        }),
        ('Email', {
            'fields': ('sent_address',),
            'classes': ('extrapretty', 'wide', 'collapse', 'in'),
            'description': _("Fields that will only be utilized if this Event will use email notifications."),
        }),
        ('Extras', {
            'fields': ('active', 'description', 'date_created', 'last_changed', ),
            'classes': ('extrapretty', 'wide', 'collapse', 'in'),
            'description': _("Additional configuration options and descriptions.")
        }),
    )
    readonly_fields = (
        'date_created', 'last_changed',
    )

    actions = [actions.activate_events, actions.deactivate_events, actions.convert_type]


@admin.register(ExternalEvent)
class ExternalEventAdmin(EventAdmin):
    inlines = [
        ExternalEventActionInLine,
    ]


@admin.register(TemporalEvent)
class TemporalEventAdmin(EventAdmin):
    pass

@admin.register(NotificationTemplate)
class NotificationTemplateAdmin(admin.ModelAdmin):
    # customize list display
    list_display = (
        '__str__',
        '_get_link_event',
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
            'description': ('Fields that will only be utilized if this is an email template.'),
        }),
        ('Extras', {
            'fields': ('active', 'description', 'date_created', 'last_changed',),
            'classes': ('extrapretty', 'wide', 'collapse', 'in'),
            'description': _("Additional configuration options and descriptions."),
        }),
    )
    readonly_fields = (
        'date_created',
        'last_changed',
    )

    actions = [actions.activate_templates, actions.deactivate_templates]

    def _get_link_event(self, obj):
        return obj.event._link_to_self()
    _get_link_event.short_description = "event"
    _get_link_event.admin_order_field = "event"


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    fieldsets = (
        (None, {
            "fields": ('event_template', 'user', 'is_artist',),
            "classes": ('extrapretty', 'wide',),
        }),
        ("Attribution", {
            "fields": ('seen', 'action_taken', 'date_of_action',),
            "classes": ('extrapretty', 'wide',),
        }),
        ("Extras", {
            "fields": ('id', 'date_created', 'last_changed',),
            "classes": ('extrapretty', 'wide', 'collapse', 'in',),
        })
    )
    readonly_fields = ('id', 'date_created', 'last_changed',)

    list_display = (
        'user',
        '_get_link_event',
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

    def _get_link_event(self, obj):
        try:
            return obj.event_template.event._link_to_self()
        except Exception:
            return None
    _get_link_event.short_description = 'event'
    _get_link_event.admin_order_field = 'event_template__event'

