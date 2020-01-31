from django.contrib import admin
from django.utils.html import format_html

from revibe.admin import check_deletion, check_display
from revibe._helpers.symbols import CROSS_MARK, CHECK_MARK

from content.admin_ext import approve_contribution, remove_delete, perform_delete
from content.models import *

# -----------------------------------------------------------------------------

# Register your models here.

@admin.register(Artist)
class ArtistAdmin(admin.ModelAdmin):
    # customize list display
    list_display = ('__str__','platform','artist_user')
    list_filter = (
        'platform',
        ('date_joined', admin.DateFieldListFilter),
    )
    # customize search
    search_fields = ['name', 'platform', 'artist_user__username'] # optional add 'song_uploaded_by__name' and 'album__uploaded_by__name'

    # other stuff
    empty_value_display = '-empty-'


@admin.register(Album)
class AlbumAdmin(admin.ModelAdmin):
    # customize list display
    list_display = ('__str__','platform','uploaded_by', '_display_status', '_deleted_status')
    list_filter = ( # reverse of display order
        ('is_deleted', admin.BooleanFieldListFilter),
        ('is_displayed', admin.BooleanFieldListFilter),
        'uploaded_by',
        'platform',
    )

    # customize search
    search_fields = ['name', 'platform', 'uploaded_by__name']

    # customize actions
    actions = [perform_delete, remove_delete]

    # other stuff
    empty_value_display = '-empty-'

    def _deleted_status(self, obj):
        return check_deletion(obj)
    
    def _display_status(self, obj):
        return check_display(obj)


@admin.register(Song)
class SongAdmin(admin.ModelAdmin):
    # customize list display
    list_display = ('__str__','platform', 'album','uploaded_by', '_display_status', '_deleted_status')
    list_filter = ('platform','album','uploaded_by',)
    # customize actions
    actions = [perform_delete, remove_delete]

    # other stuff
    empty_value_display = '-empty-'

    def _deleted_status(self, obj):
        return check_deletion(obj)
    
    def _display_status(self, obj):
        return check_display(obj)


@admin.register(AlbumContributor)
class AlbumContributorAdmin(admin.ModelAdmin):
    # customize list display
    list_display = ('__str__','album', 'artist', 'contribution_type')
    list_filter = (
        ('album__uploaded_by', admin.RelatedOnlyFieldListFilter),
        ('album', admin.RelatedOnlyFieldListFilter),
        ('artist', admin.RelatedFieldListFilter),
        'contribution_type',
        ('primary_artist', admin.BooleanFieldListFilter),
    )
    # customize actions
    actions = [approve_contribution,]

    # other stuff
    empty_value_display = '-empty-'


@admin.register(SongContributor)
class SongContributorAdmin(admin.ModelAdmin):
    # customize list display
    list_display = ('__str__', 'song', 'artist', 'contribution_type')
    list_filter = (
        ('song__uploaded_by', admin.RelatedOnlyFieldListFilter),
        ('song', admin.RelatedOnlyFieldListFilter),
        ('artist', admin.RelatedFieldListFilter),
        'contribution_type',
        ('primary_artist', admin.BooleanFieldListFilter),
    )
    # customize actions
    actions = [approve_contribution]

    # other stuff
    empty_value_display = '-empty-'


@admin.register(Image)
class ImageAdmin(admin.ModelAdmin):
    # customize list display
    list_display = ('__str__', 'object', 'width', 'height')
    list_filter = (
        ('is_original', admin.BooleanFieldListFilter),
    )

    # other stuff
    empty_value_display = '-empty-'

    def object(self, o):
        return f"{o.obj.__class__.__name__} - {o.obj}"


@admin.register(Track)
class TrackAdmin(admin.ModelAdmin):
    # customize list display
    list_display = ('__str__', 'song',)
    list_filter = (
        ('is_original', admin.BooleanFieldListFilter),
    )

    # other stuff
    empty_value_display = '-empty-'

