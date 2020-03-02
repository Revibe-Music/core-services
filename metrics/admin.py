from django.contrib import admin

from metrics.models import *

# -----------------------------------------------------------------------------

@admin.register(Stream)
class StreamAdmin(admin.ModelAdmin):
    pass


@admin.register(Search)
class SearchAdmin(admin.ModelAdmin):
    pass


@admin.register(AppSession)
class AppSessionAdmin(admin.ModelAdmin):
    # customize list display
    list_display = ('__str__', 'interactions', '_display_session_time')

    def _display_session_time(self, obj):
        return f"{round(obj.session_time, 2)} minutes"
    _display_session_time.short_description = "session minutes"

