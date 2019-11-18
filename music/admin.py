from django.contrib import admin
from .models import *

admin.site.register(Artist)
admin.site.register(Album)
admin.site.register(AlbumContributor)
admin.site.register(Song)
admin.site.register(SongContributor)
admin.site.register(Library)
admin.site.register(Playlist)
admin.site.register(LibrarySongs)
admin.site.register(PlaylistSongs)
