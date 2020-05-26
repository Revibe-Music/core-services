from django.contrib import admin
from django.utils.html import format_html

from revibe.admin import check_deletion, check_display
from revibe._helpers.symbols import CROSS_MARK, CHECK_MARK

from accounts.admin_ext.inlines import ArtistProfileInline
from content import browse
from content.admin_ext import (
    approve_contribution, remove_delete, perform_delete, reprocess_song, reprocess_image, update_mailchimp_info,
    inlines
)
from content.models import *

# -----------------------------------------------------------------------------

# Register your models here.

@admin.register(Artist)
class ArtistAdmin(admin.ModelAdmin):
    fieldsets = (
        (None, {
            "fields": ('name', 'platform',),
            "classes": ('extrapretty', 'wide',),
        }),
        ("Extras", {
            "fields": ('id', 'uri', 'date_joined', 'last_changed',),
            "classes": ('extrapretty', 'wide', 'collapse', 'in',),
        })
    )
    readonly_fields = (
        'id', 'uri',
        'date_joined', 'last_changed',
    )

    _inlines = []

    list_display = ('sortable_str','platform','_link_to_user')
    list_filter = (
        'platform',
        ('date_joined', admin.DateFieldListFilter),
    )

    search_fields = ['name', 'platform', 'artist_user__username'] # optional add 'song_uploaded_by__name' and 'album__uploaded_by__name'

    actions = [reprocess_image, update_mailchimp_info]

    empty_value_display = '-empty-'

    def sortable_str(self, obj):
        return obj.__str__()
    sortable_str.short_description = 'artist'
    sortable_str.admin_order_field = 'name'

    def _link_to_user(self, obj):
        try:
            return obj.artist_user._link_to_self()
        except Exception:
            return None
    _link_to_user.short_description = "user"
    _link_to_user.admin_order_field = "artist_user"


    def get_form(self, request, obj=None, **kwargs):
        # add the Artist Profile inline IF the artist is a Revibe artist
        # otherwise reset the inlines
        if (obj) and (obj.platform == 'Revibe'):
            self.inlines = self._inlines + [ArtistProfileInline,]
        else:
            self.inlines = self._inlines

        return super().get_form(request, obj, **kwargs)



@admin.register(Album)
class AlbumAdmin(admin.ModelAdmin):

    fieldsets = (
        (None, {
            "fields": ('name', 'type', 'date_published', 'uploaded_by', 'platform',),
            "classes": ('extrapretty', 'wide',),
        }),
        ("Extras", {
            "fields": ('id', 'uri', 'is_displayed', 'is_deleted', 'uploaded_date', 'last_changed', )
        })
    )
    readonly_fields = (
        'id', 'uri',
        'uploaded_date', 'last_changed',
    )

    inlines = [
        inlines.AlbumContributorInline,
        inlines.AlbumGenreInline,
        inlines.AlbumTagInline,
    ]

    list_display = ('sortable_str','platform','uploaded_by', '_display_status', '_deletion_status')
    list_filter = ( # reverse of display order
        ('is_deleted', admin.BooleanFieldListFilter),
        ('is_displayed', admin.BooleanFieldListFilter),
        'uploaded_by',
        'platform',
    )

    search_fields = ['name', 'platform', 'uploaded_by__name']

    actions = [perform_delete, remove_delete, reprocess_image]

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
    fieldsets = (
        (None, {
            "fields": ('title', 'duration', 'is_explicit', 'uploaded_by', 'album', 'album_order', 'platform',),
            "classes": ('extrapretty', 'wide'),
        }),
        ("Extras", {
            "fields": ('id', 'uri', 'isrc_code', 'is_displayed', 'is_deleted', 'uploaded_date', 'last_changed',)
        })
    )
    readonly_fields = (
        'id', 'uri',
        'uploaded_date', 'last_changed',
    )

    inlines = [
        inlines.SongContributorInline,
        inlines.SongGenreInline,
        inlines.SongTagInline,
    ]

    list_display = (
        'sortable_str',
        'platform',
        'album',
        'uploaded_by',
        '_display_status',
        '_deletion_status',
        # 'get_original_track',
        '_number_of_tracks',
    )
    list_filter = (
        ('is_deleted', admin.BooleanFieldListFilter),
        ('is_displayed', admin.BooleanFieldListFilter),
        ('album', admin.RelatedOnlyFieldListFilter),
        ('uploaded_by', admin.RelatedOnlyFieldListFilter),
        # 'genre',
        'platform',
    )

    search_fields = ['title', 'album__name', 'uploaded_by__name',]

    actions = [perform_delete, remove_delete, reprocess_song]

    empty_value_display = '-empty-'

    def _deletion_status(self, obj):
        return check_deletion(obj)
    
    def _display_status(self, obj):
        return check_display(obj)
    
    def get_original_track(self, obj):
        ts = obj.tracks.filter(is_original=True)
        if len(ts) > 0:
            return ts[0]._link_url()
        return None
    get_original_track.short_description = 'original track'

    def _number_of_tracks(self, obj):
        return obj.tracks.all().count()
    _number_of_tracks.short_description = 'tracks'

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
    search_fields = ['song__title', 'song__uploaded_by__name']

    # other stuff
    empty_value_display = '-empty-'


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    pass


@admin.register(Genre)
class GenreAdmin(admin.ModelAdmin):
    pass


@admin.register(PlaceholderContribution)
class PlaceholderContributionAdmin(admin.ModelAdmin):
    pass

# class TopSongsAdmin(SongAdmin):
#     def get_queryset(self, request):
#         return browse.top_songs_all_time()

class BaseSearchAdmin(admin.ModelAdmin):
    fieldsets = (
        (None, {
            "fields": ('field', 'type', 'order',),
            "classes": ('extrapretty', 'wide',),
        }),
        ("Extras", {
            "fields": ('id', 'active', 'description', 'date_created', 'last_changed',),
            "classes": ('extrapretty', 'wide', 'collapse', 'in',),
        })
    )
    readonly_fields = (
        'id',
        'date_created', 'last_changed',
    )

    list_display = (
        'field',
        'type',
        'order',
        'active',
    )
    list_filter = (
        'type',
        'active',
    )

    


@admin.register(Search)
class SearchAdmin(BaseSearchAdmin):
    fieldsets = BaseSearchAdmin.fieldsets
    fieldsets[0][1]["fields"] = ('model',) + fieldsets[0][1]["fields"]

    def get_list_display(self, request):
        normal_thing = super().get_list_display(request)

        return normal_thing[:1] + ('model',) + normal_thing[1:]

    def get_list_filter(self, request):
        result = super().get_list_filter(request)
        return ('model',) + result

# @admin.register(AlbumSearch)
# class AlbumSearchAdmin(BaseSearchAdmin):
#     pass

# @admin.register(ArtistSearch)
# class ArtistSearchAdmin(BaseSearchAdmin):
#     pass

# @admin.register(GenreSearch)
# class GenreSearchAdmin(BaseSearchAdmin):
#     pass

# @admin.register(SongSearch)
# class SongSearchAdmin(BaseSearchAdmin):
#     pass

# @admin.register(TagSearch)
# class TagSearchAdmin(BaseSearchAdmin):
#     pass



