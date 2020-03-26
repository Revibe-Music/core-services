from django.contrib import admin

from revibe.admin import html_check_x

from music.models import *

# -----------------------------------------------------------------------------

@admin.register(Library)
class LibraryAdmin(admin.ModelAdmin):
    # customize list display
    list_display = ('__str__', 'user')
    list_filter = ('platform',)


@admin.register(Playlist)
class PlaylistAdmin(admin.ModelAdmin):
    # customize list display
    list_display = ('__str__', 'user', 'html_public')
    list_filter = (
        ('is_public', admin.BooleanFieldListFilter),
        ('revibe_curated', admin.BooleanFieldListFilter),
    )

    # customize search
    search_fields = ['user__username', 'name']

    def html_public(self, obj):
        return html_check_x(obj, 'is_public')
    html_public.short_description = 'public status'
    html_public.admin_order_field = 'is_public'


@admin.register(LibrarySong)
class LibrarySongAdmin(admin.ModelAdmin):
    pass


@admin.register(PlaylistSong)
class PlaylistSongAdmin(admin.ModelAdmin):
    pass

