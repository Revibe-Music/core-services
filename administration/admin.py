from django.contrib import admin

from revibe.admin import html_check_x
from revibe.utils.language import text

from administration.admin_ext import test_api_key, reset_user_count
from administration.models import *

# -----------------------------------------------------------------------------

# Register your models here.

@admin.register(ContactForm)
class ContactFormAdmin(admin.ModelAdmin):
    # customize list display
    list_display = ('__str__', 'assigned_to', 'get_resolution')
    list_filter = (
        ('assigned_to', admin.RelatedFieldListFilter),
        'subject',
        ('resolved', admin.BooleanFieldListFilter),
    )

    # customize search
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
    # customize list display
    list_display = ('__str__', '_budget', '_spent', 'create_url',)
    # list_filter = (,)

    # customize search
    search_fields = ['name']


@admin.register(YouTubeKey)
class YoutubeKeyAdmin(admin.ModelAdmin):
    # customize list display
    list_display = ('sortable_str', 'point_budget', 'number_of_users', )

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


@admin.register(Alert)
class AlertAdmin(admin.ModelAdmin):
    pass


@admin.register(AlertSeen)
class AlertSeenAdmin(admin.ModelAdmin):
    pass


@admin.register(ArtistSpotlight)
class ArtistSpotlightAdmin(admin.ModelAdmin):
    pass


@admin.register(Blog)
class BlogAdmin(admin.ModelAdmin):
    # customize list display
    list_display = ('sortable_str', 'body_trunc', 'author', 'publish_date', )
    list_filter = (
        'category',
        ('author', admin.RelatedOnlyFieldListFilter),
        ('publish_date', admin.DateFieldListFilter),
    )

    # customize search
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
    # customize list display
    list_display = ('key', 'value')

    # customize search
    search_fields = [
        'key',
        'value',
    ]


# general admin information and changes
admin.site.empty_value_display = "-empty-"
admin.site.site_header = "Revibe Administration"
admin.site.index_title = "Revibe"
admin.site.site_title = "Revibe Administration"
admin.site.site_url = "/hc/"