from django.contrib import admin
from django.utils.html import format_html

from revibe.admin import check_deletion, check_display
from revibe._helpers.symbols import CROSS_MARK, CHECK_MARK

from content.admin_ext import (
    approve_contribution, remove_delete, perform_delete, reprocess_song
)
from content.models import *

# -----------------------------------------------------------------------------

# Register your models here.

@admin.register(Artist)
class ArtistAdmin(admin.ModelAdmin):
    # customize list display
    list_display = ('sortable_str','platform','artist_user')
    list_filter = (
        'platform',
        ('date_joined', admin.DateFieldListFilter),
    )
    # customize search
    search_fields = ['name', 'platform', 'artist_user__username'] # optional add 'song_uploaded_by__name' and 'album__uploaded_by__name'

    # other stuff
    empty_value_display = '-empty-'

    def sortable_str(self, obj):
        return obj.__str__()
    sortable_str.short_description = 'artist'
    sortable_str.admin_order_field = 'name'


@admin.register(Album)
class AlbumAdmin(admin.ModelAdmin):
    # customize list display
    list_display = ('sortable_str','platform','uploaded_by', '_display_status', '_deletion_status')
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

    def _deletion_status(self, obj):
        return check_deletion(obj)
    
    def _display_status(self, obj):
        return check_display(obj)
    
    def sortable_str(self, obj):
        return obj.__str__()
    sortable_str.short_description = 'album'
    sortable_str.admin_order_field = 'name'


@admin.register(Song)
class SongAdmin(admin.ModelAdmin):
    # customize list display
    list_display = ('sortable_str','platform', 'album','uploaded_by', '_display_status', '_deletion_status', 'get_original_track')
    list_filter = (
        ('is_deleted', admin.BooleanFieldListFilter),
        ('is_displayed', admin.BooleanFieldListFilter),
        ('album', admin.RelatedOnlyFieldListFilter),
        ('uploaded_by', admin.RelatedOnlyFieldListFilter),
        'genre',
        'platform',
    )

    # customize search
    search_fields = ['title', 'album__name', 'uploaded_by__name',]

    # customize actions
    actions = [perform_delete, remove_delete, reprocess_song]

    # other stuff
    empty_value_display = '-empty-'

    def _deletion_status(self, obj):
        return check_deletion(obj)
    
    def _display_status(self, obj):
        return check_display(obj)
    
    def get_original_track(self, obj):
        ts = obj.tracks.filter(is_original=True)
        if len(ts) > 0:
            controls = ts[0]._audio_controls()
            return controls
        return None
    get_original_track.short_description = 'original track'

    def sortable_str(self, obj):
        return obj.__str__()
    sortable_str.short_description = 'song'
    sortable_str.admin_order_field = 'title'


@admin.register(AlbumContributor)
class AlbumContributorAdmin(admin.ModelAdmin):
    # customize list display
    list_display = ('__str__','album', 'artist', 'contribution_type')
    list_filter = (
        ('primary_artist', admin.BooleanFieldListFilter),
        ('artist', admin.RelatedFieldListFilter),
        ('album', admin.RelatedOnlyFieldListFilter),
        ('album__uploaded_by', admin.RelatedOnlyFieldListFilter),
        'contribution_type',
    )

    # customize search
    search_fields = ['album__name', 'album__uploaded_by__name','artist__name']

    # customize actions
    actions = [approve_contribution,]

    # other stuff
    empty_value_display = '-empty-'


@admin.register(SongContributor)
class SongContributorAdmin(admin.ModelAdmin):
    # customize list display
    list_display = ('__str__', 'song', 'artist', 'contribution_type')
    list_filter = (
        ('primary_artist', admin.BooleanFieldListFilter),
        ('artist', admin.RelatedFieldListFilter),
        ('song', admin.RelatedOnlyFieldListFilter),
        ('song__uploaded_by', admin.RelatedOnlyFieldListFilter),
        'contribution_type',
    )

    # customize search
    search_fields = ['song__title', 'song__uploaded_by__name', 'artist__name']

    # customize actions
    actions = [approve_contribution]

    # other stuff
    empty_value_display = '-empty-'


@admin.register(Image)
class ImageAdmin(admin.ModelAdmin):
    # customize list display
    list_display = ('__str__', '_object', 'dimensions', '_link_url')
    list_filter = (
        ('is_original', admin.BooleanFieldListFilter),
    )

    # customize search
    search_fields = ['album__name', 'artist__name']

    # other stuff
    empty_value_display = '-empty-'

    def _object(self, o):
        return f"{o.obj.__class__.__name__} - {o.obj}"
    _object.short_description = "related object"


@admin.register(Track)
class TrackAdmin(admin.ModelAdmin):
    # customize list display
    list_display = ('__str__', 'song', '_link_url')
    list_filter = (
        ('is_original', admin.BooleanFieldListFilter),
    )

    # customize search
    search_fields = ['song__title', 'song__uploaded_by']

    # other stuff
    empty_value_display = '-empty-'

