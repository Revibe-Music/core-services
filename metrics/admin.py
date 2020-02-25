from django.contrib import admin

from metrics.models import *

# -----------------------------------------------------------------------------

@admin.register(Stream)
class StreamAdmin(admin.ModelAdmin):
    pass
