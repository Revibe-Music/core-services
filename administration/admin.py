from django.contrib import admin

from administration.models import *

# -----------------------------------------------------------------------------

# Register your models here.

admin.site.register(ContactForm)


admin.site.register(Campaign)


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



# general admin information and changes
admin.site.empty_value_display = "-empty-"
admin.site.site_header = "Revibe Administration"
admin.site.index_title = "Revibe"
admin.site.site_title = "Revibe Administration"
admin.site.site_url = "/hc/"
