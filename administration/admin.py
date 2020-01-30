from django.contrib import admin

from administration.models import *

# -----------------------------------------------------------------------------

# Register your models here.

admin.site.register(ContactForm)
admin.site.register(Campaign)
admin.site.register(YouTubeKey)



# general admin information and changes
admin.site.empty_value_display = "-empty-"
admin.site.site_header = "Revibe Administration"
admin.site.index_title = "Revibe"
admin.site.site_title = "Revibe Administration"
admin.site.site_url = "/hc/"
