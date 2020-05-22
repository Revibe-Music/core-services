"""
Created: 22 May 2020
Author: Jordan Prechac
"""

from django.contrib import admin

from music.models import Playlist, PlaylistSong

from .forms import PlaylistSongInlineForm

# -----------------------------------------------------------------------------


class PlaylistFollowerInline(admin.TabularInline):
    model = Playlist.followers.through

    extra = 1

    verbose_name = "follower"
    verbose_name_plural = "followers"

class PlaylistSongInline(admin.TabularInline):
    model = PlaylistSong
    form = PlaylistSongInlineForm
    readonly_fields = ('date_saved',)

    extra = 1

    verbose_name = "song"
    verbose_name_plural = "songs"

