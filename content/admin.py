from django.contrib import admin

from content.models import *

# Register your models here.
admin.site.register(Artist)
admin.site.register(Album)
admin.site.register(Song)
admin.site.register(AlbumContributor)
admin.site.register(SongContributor)
admin.site.register(Image)
admin.site.register(Track)