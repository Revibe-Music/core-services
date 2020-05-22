from django.contrib import admin

from revibe.admin import html_check_x

from music.models import *
from music.utils.admin import inlines

# -----------------------------------------------------------------------------

@admin.register(Library)
class LibraryAdmin(admin.ModelAdmin):
    # customize list display
    list_display = ('__str__', 'user')
    list_filter = ('platform',)


@admin.register(Playlist)
class PlaylistAdmin(admin.ModelAdmin):
    fieldsets = (
        (None, {
            "fields": ('name', 'user', 'description',),
            "classes": ('extrapretty', 'wide',),
        }),
        ("Staff", {
            "fields": ('is_public', 'revibe_curated', 'show_on_browse',),
            "classes": ('extrapretty', 'wide',),
        }),
        ("Extras", {
            "fields": ('id', 'date_created', 'last_changed',),
            "classes": ('extrapretty', 'wide', 'collapse', 'in',),
        })
    )
    readonly_fields = ('id', 'date_created', 'last_changed',)

    inlines = [
        inlines.PlaylistSongInline,
        inlines.PlaylistFollowerInline,
    ]

    list_display = (
        'name',
        '_link_to_user',
        'is_public',
    )
    list_filter = (
        ('is_public', admin.BooleanFieldListFilter),
        ('revibe_curated', admin.BooleanFieldListFilter),
    )

    search_fields = ['user__username', 'name']

    def _link_to_user(self, obj):
        user = getattr(obj, 'user', None)
        if user == None:
            return None
        
        return user._link_to_self()
    _link_to_user.short_description = "user"
    _link_to_user.admin_order_field = "user"


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

