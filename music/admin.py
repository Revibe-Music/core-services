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
    # customize list display
    list_display = (
        '__str__',
        '_display_song',
        '_display_playlist',
    )
    list_filter = (
        ('playlist__is_public', admin.BooleanFieldListFilter),
        ('playlist__revibe_curated', admin.BooleanFieldListFilter),
        ('playlist__show_on_browse', admin.BooleanFieldListFilter),
        ('playlist', admin.RelatedOnlyFieldListFilter),
        ('song', admin.RelatedOnlyFieldListFilter),
    )


    # functions
    def _display_song(self, obj):
        return str(obj.song)
    _display_song.short_description = 'song'
    _display_song.admin_order_field = 'song__title'

    def _display_playlist(self, obj):
        return str(obj.playlist)
    _display_playlist.short_description = 'playlist'
    _display_playlist.admin_order_field = 'playlits__name'

