from django.contrib import admin

from metrics.models import *

# -----------------------------------------------------------------------------

@admin.register(Stream)
class StreamAdmin(admin.ModelAdmin):
    # customize list display
    list_display = (
        '__str__',
        'song',
        'user',
        'source',
    )
    list_filter = (
        'source',
        ('song', admin.RelatedOnlyFieldListFilter),
        ('user', admin.RelatedOnlyFieldListFilter),
        'alternate_platform',
        ('timestamp', admin.DateFieldListFilter),
        ('is_downloaded', admin.BooleanFieldListFilter),
        ('is_saved', admin.BooleanFieldListFilter),
    )

    # customize search
    search_fields = [
        'song__title',
        'user__username'
    ]


@admin.register(Search)
class SearchAdmin(admin.ModelAdmin):
    # customize list display
    list_display = (
        '__str__',
        'user',
    )
    list_filter = (
        'search_text',
        ('user', admin.RelatedOnlyFieldListFilter),
        ('timestamp', admin.DateFieldListFilter)
    )


@admin.register(AppSession)
class AppSessionAdmin(admin.ModelAdmin):
    # customize list display
    list_display = ('__str__', 'interactions', '_display_session_time')

    def _display_session_time(self, obj):
        return f"{round(obj.session_time, 2)} minutes"
    _display_session_time.short_description = "session minutes"

