from django.contrib import admin
from .models import *

admin.site.register(Artist)
admin.site.register(Album)
admin.site.register(AlbumContributors)
admin.site.register(Song)
admin.site.register(SongContributors)
admin.site.register(Library)
admin.site.register(Playlist)
