from django.contrib import admin

from content.admin_ext import perform_delete, remove_delete
from content.models import *

# -----------------------------------------------------------------------------

# admin actions

# Admin Models
class ArtistAdmin(admin.ModelAdmin):
    # customize list display
    list_display = ('name','platform',)
    list_filter = ('platform',)


class AlbumAdmin(admin.ModelAdmin):
    # customize list display
    list_display = ('name','platform','uploaded_by')
    list_filter = ('platform','uploaded_by')
    # customize actions
    actions = [perform_delete, remove_delete]


class SongAdmin(admin.ModelAdmin):
    # customize list display
    list_display = ('title','platform', 'album','uploaded_by')
    list_filter = ('platform','album','uploaded_by')
    # customize actions
    actions = [perform_delete, remove_delete]

# Register your models here.
admin.site.register(Artist, ArtistAdmin)
admin.site.register(Album, AlbumAdmin)
admin.site.register(Song, SongAdmin)
admin.site.register(AlbumContributor)
admin.site.register(SongContributor)
admin.site.register(Image)
admin.site.register(Track)