from django.contrib import admin

from revibe.admin import html_check_x

from administration.admin_ext import test_api_key
from administration.models import *

# -----------------------------------------------------------------------------

# Register your models here.

@admin.register(ContactForm)
class ContactFormAdmin(admin.ModelAdmin):
    # customize list display
    list_display = ('__str__', 'assigned_to', 'get_resolution')

    def get_resolution(self, obj):
        return html_check_x(obj, 'resolved')
    get_resolution.short_description = 'resolved'
    get_resolution.admin_order_field = 'resolved'


@admin.register(Campaign)
class CampaingAdmin(admin.ModelAdmin):
    # customize list display
    list_display = ('__str__', '_budget', '_spent', 'create_url',)


@admin.register(YouTubeKey)
class YoutubeKeyAdmin(admin.ModelAdmin):
    # customize list display
    list_display = ('sortable_str', 'point_budget',)
    list_filter = (
        ('worked_on_last_test', admin.BooleanFieldListFilter),
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
    actions = [test_api_key]


# general admin information and changes
admin.site.empty_value_display = "-empty-"
admin.site.site_header = "Revibe Administration"
admin.site.index_title = "Revibe"
admin.site.site_title = "Revibe Administration"
admin.site.site_url = "/hc/"