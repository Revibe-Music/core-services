from django.contrib import admin

from content.admin_ext import approve_contribution, remove_delete, perform_delete
from content.models import *

# -----------------------------------------------------------------------------

# Register your models here.

@admin.register(Artist)
class ArtistAdmin(admin.ModelAdmin):
    # customize list display
    list_display = ('__str__','platform','artist_user')
    list_filter = ('platform',)

    empty_value_display = '-empty-'


@admin.register(Album)
class AlbumAdmin(admin.ModelAdmin):
    # customize list display
    list_display = ('__str__','platform','uploaded_by')
    list_filter = ('platform','uploaded_by')
    # customize detail display
    # fields = ()
    # customize actions
    actions = [perform_delete, remove_delete]
    
    empty_value_display = '-empty-'


@admin.register(Song)
class SongAdmin(admin.ModelAdmin):
    # customize list display
    list_display = ('__str__','platform', 'album','uploaded_by')
    list_filter = ('platform','album','uploaded_by')
    # customize actions
    actions = [perform_delete, remove_delete]

    empty_value_display = '-empty-'


@admin.register(AlbumContributor)
class AlbumContributorAdmin(admin.ModelAdmin):
    # customize actions
    actions = [approve_contribution,]

    empty_value_display = '-empty-'


@admin.register(SongContributor)
class SongContributorAdmin(admin.ModelAdmin):
    # customize actions
    actions = [approve_contribution]

    empty_value_display = '-empty-'


@admin.register(Image)
class ImageAdmin(admin.ModelAdmin):
    # customize list display
    list_display = ('__str__', 'get_object2')

    empty_value_display = '-empty-'

    def get_object2(self, o):
        return f"{o.obj.__class__.__name__} - {o.obj}"


@admin.register(Track)
class TrackAdmin(admin.ModelAdmin):
    # customize list display
    list_display = ('__str__', 'get_object2')

    empty_value_display = '-empty-'

    def get_object2(self, o):
        return f"{o.song.__class__.__name__} - {o.song}"

