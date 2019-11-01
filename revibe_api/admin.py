from django.contrib import admin
from revibe_api.models import *

# Register your models here.
admin.site.register(CustomUser)
admin.site.register(Profile)
admin.site.register(Artist)
admin.site.register(Album)
admin.site.register(AlbumContributors)
admin.site.register(Song)
admin.site.register(SongContributors)
admin.site.register(Library)
admin.site.register(Playlist)
admin.site.register(Social)

