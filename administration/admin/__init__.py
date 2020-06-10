from django.contrib import admin

from revibe.admin import html_check_x
from revibe.utils.language import text

from administration.models import *

from . import inlines
from .actions import test_api_key, reset_user_count

# -----------------------------------------------------------------------------

# Register your models here.

@admin.register(ContactForm)
class ContactFormAdmin(admin.ModelAdmin):
    fieldsets = (
        (None, {
            "fields": ('id', 'subject', 'message',),
            "classes": ('extrapretty', 'wide',),
        }),
        ("User Info", {
            "fields": ('user', 'first_name', 'last_name', 'email',),
            "classes": ('extrapretty', 'wide',),
        }),
        ("Staff Info", {
            "fields": ('assigned_to', 'priority', 'resolved',),
            "classes": ('extrapretty', 'wide',),
        }),
        ("Extras", {
            "fields": ('date_created', 'last_changed',),
            "classes": ('extrapretty', 'wide', 'collapse', 'in',),
        })
    )
    readonly_fields = ('id', 'date_created', 'last_changed',)

    list_display = (
        '__str__',
        'assigned_to',
        'priority',
        'resolved',
        # 'date_created',
    )
    list_filter = (
        ('resolved', admin.BooleanFieldListFilter),
        ('assigned_to', admin.RelatedFieldListFilter),
        'priority',
    )

    search_fields = [
        'message',
        'subject',
        'assigned_to',
    ]

    def get_resolution(self, obj):
        return html_check_x(obj, 'resolved')
    get_resolution.short_description = 'resolved'
    get_resolution.admin_order_field = 'resolved'


@admin.register(Campaign)
class CampaingAdmin(admin.ModelAdmin):
    fieldsets = (
        (None, {
            "fields": ('name', 'budget', 'spent', 'destination',),
            "classes": ('extrapretty', 'wide',),
        }),
        ("Extras", {
            "fields": ('uri', 'date_created', 'last_changed',),
            "classes": ('extrapretty', 'wide', 'collapse', 'in',),
        }),
    )
    readonly_fields = ('date_created', 'last_changed',)

    list_display = (
        '__str__',
        '_budget',
        '_spent',
        'create_url',
    )
    # list_filter = (,)

    search_fields = ['name']


@admin.register(YouTubeKey)
class YoutubeKeyAdmin(admin.ModelAdmin):
    fieldsets = (
        (None, {
            "fields": ('key', 'point_budget', 'number_of_users',),
            "classes": ('extrapretty', 'wide',),
        }),
        ("Extras", {
            "fields": ('id', 'last_date_broken', 'date_created', 'last_changed',),
            "classes": ('extrapretty', 'wide', 'collapse', 'in',),
        })
    )
    readonly_fields = ('id', 'last_date_broken', 'date_created', 'last_changed',)

    list_display = (
        'sortable_str',
        'point_budget',
        'number_of_users',
    )

    def sortable_str(self, obj):
        """
        Provides a field that replicates the classes __str__ method,
        but also allows for adding a sort field
        """
        return obj.__str__()
    sortable_str.short_description = 'API Key'
    sortable_str.admin_order_field = 'key'

    # customize search
    search_fields = ['key']

    # actions
    actions = [test_api_key, reset_user_count]


# @admin.register(Alert)
class AlertAdmin(admin.ModelAdmin):
    fieldsets = (
        (None, {
            "fields": ('subject', 'message', 'category',),
            "classes": ('extrapretty', 'wide', ),
        }),
        ("Scheduling", {
            "fields": ('start_date', 'end_date', 'enabled',),
            "classes": ('extrapretty', 'wide',),
        }),
        ("Extras", {
            "fields": ('id', 'date_created', 'last_changed',),
            "classes": ('extrapretty', 'wide', 'collapse', 'in',),
        })
    )
    readonly_fields = ('id', 'date_created', 'last_changed',)

    list_display = (
        'subject',
        'message',
        'category',
    )
    list_filter = (
        ('enabled', admin.BooleanFieldListFilter),
    )


# @admin.register(AlertSeen)
class AlertSeenAdmin(admin.ModelAdmin):
    pass


@admin.register(ArtistOfTheWeek)
class ArtistOfTheWeekAdmin(admin.ModelAdmin):
    fieldsets = (
        (None, {
            "fields": ('artist', 'start_date', 'statement', 'highlighted_album'),
            "classes": ('extrapretty', 'wide',),
        }),
        ("Extras", {
            "fields": ('active', 'description', 'date_created', 'last_changed', 'id',),
        })
    )
    readonly_fields = (
        'id',
        'date_created', 'last_changed',
    )

    list_display = (
        'artist',
        'start_date',
        'active',
    )
    list_filter = (
        ('start_date', admin.DateFieldListFilter),
        ('active', admin.BooleanFieldListFilter),
    )

    inlines = [
        inlines.ArtistOfTheWeekImageInline,
    ]


@admin.register(ArtistSpotlight)
class ArtistSpotlightAdmin(admin.ModelAdmin):
    fieldsets = (
        (None, {
            "fields": ('artist', 'date',),
            "classes": ('extrapretty', 'wide',),
        }),
        ("Extras", {
            "fields": ('description', 'date_created', 'last_changed',),
            "classes": ('extrapretty', 'wide', 'collapse', 'in',),
        })
    )
    readonly_fields = ('date_created', 'last_changed',)

    list_display = (
        'artist',
        'date',
    )

    search_fields = [
        'artist__name',
    ]


@admin.register(Blog)
class BlogAdmin(admin.ModelAdmin):
    fieldsets = (
        (None, {
            "fields": ('category', 'title', 'body', 'summary', 'header_image', 'side_image',),
            "classes": ('extrapretty', 'wide',),
        }),
        ("Publish Info", {
            "fields": ('publish_date', 'author', 'artist', 'display_style',),
            "classes": ('extrapretty', 'wide',),
        }),
        ("Extras", {
            "fields": ('id', 'date_created', 'last_changed',),
            "classes": ('extrapretty', 'wide', 'collapse', 'in',),
        })
    )
    readonly_fields = ('id', 'date_created', 'last_changed',)

    list_display = (
        'title',
        'body_trunc',
        'author',
        'publish_date',
    )
    list_filter = (
        ('tags', admin.RelatedOnlyFieldListFilter),
        ('publish_date', admin.DateFieldListFilter),
        ('author', admin.RelatedOnlyFieldListFilter),
        'category',
    )

    inlines = [ # add 'artists' and 'tags'
        inlines.BlogArtistsInline,
        inlines.BlogTagInline,
    ]

    search_fields = [
        'title',
        'body',
        'summary',
    ]


    # functions
    def sortable_str(self, obj):
        return obj.__str__()
    sortable_str.short_description = 'blog post'
    sortable_str.admin_order_field = 'title'

    def body_trunc(self, obj):
        return text.truncate_string(obj.body)
    body_trunc.short_description = 'body'
    body_trunc.admin_order_field = 'body'

    def display_author(self, obj):
        try:
            return f"{obj.first_name} {obj.last_name}"
        except Exception:
            return str(obj)


@admin.register(BlogTag)
class BlogTagAdmin(admin.ModelAdmin):
    # customize search
    search_fields = ['text',]


@admin.register(Variable)
class VariableAdmin(admin.ModelAdmin):
    fieldsets = (
        (None, {
            "fields": ('key', 'value', 'rules', 'category',),
            "classes": ('extrapretty', 'wide',)
        }),
        ("Extras", {
            "fields": ('id', 'active', 'date_created', 'last_changed',),
            "classes": ('extrapretty', 'wide', 'collapse', 'id',),
        })
    )
    readonly_fields = (
        'id',
        'date_created', 'last_changed',
    )

    list_display = (
        'key',
        'value',
        'active',
    )
    list_filter = (
        ('active', admin.BooleanFieldListFilter),
        'category',
    )

    search_fields = [
        'key',
        'value',
        'category',
    ]


@admin.register(ArtistAnalyticsCalculation)
class ArtistAnalyticsCalculationAdmin(admin.ModelAdmin):
    # customize list display
    list_display = (
        '__str__',
        'root_object',
        '_calculation',
        'distinct',
    )
    list_filter = (
        'root_object',
        '_calculation',
    )


# @admin.register(Survey)
class SurveyAdmin(admin.ModelAdmin):
    pass


# general admin information and changes
admin.site.empty_value_display = "-empty-"
admin.site.site_header = "Revibe Administration"
admin.site.index_title = "Revibe"
admin.site.site_title = "Revibe Administration"
admin.site.site_url = "/hc/"