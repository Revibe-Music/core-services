from django.contrib import admin

from music.models import *

admin.site.register(Library)
admin.site.register(Playlist)
admin.site.register(LibrarySong)
admin.site.register(PlaylistSong)
