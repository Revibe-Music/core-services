from django.contrib import admin

from accounts.admin_ext import actions
from accounts.models import *

# -----------------------------------------------------------------------------

# Register your models here.

@admin.register(CustomUser)
class CustomUserAdmin(admin.ModelAdmin):
    # customize list display
    list_display = ('__str__', '_full_name', 'date_joined', 'id')
    list_filter = (
        ('date_joined', admin.DateFieldListFilter),
        ('is_staff', admin.BooleanFieldListFilter),
        ('programmatic_account', admin.BooleanFieldListFilter),
    )

    # customize search
    search_fields = ['username', 'first_name', 'last_name']

    # customize actions
    actions = [actions.update_mailchimp_info]#[change_password]

    def _full_name(self, obj):
        return f"{obj.first_name} {obj.last_name}"


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    # customize list display
    list_display = ('__str__', 'email', 'user')
    list_filter = (
        ('user__is_staff', admin.BooleanFieldListFilter),
        ('campaign', admin.RelatedOnlyFieldListFilter),
        ('allow_email_marketing', admin.BooleanFieldListFilter),
    )

    # customize search
    search_fields = ['user__username', 'user__first_name', 'user__last_name', 'email']


@admin.register(Social)
class SocialAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'user', 'platform')


@admin.register(ArtistProfile)
class ArtistProfileAdmin(admin.ModelAdmin):
    # customize list display
    list_display = ('__str__', 'artist', 'email', 'get_artist_username')
    list_filter = (
        'city',
        'state',
        'country',
    )

    # customize search
    search_fields = ['artist__name', 'email',]

    def get_artist_username(self, obj):
        return obj.artist.artist_user.username
    get_artist_username.short_description = 'username'


@admin.register(SocialMedia)
class SocialMediaAdmin(admin.ModelAdmin):
    # customize list display
    list_display = ("_sortable_str", "_get_artist",)

    def _sortable_str(self, obj):
        return obj.__str__()
    _sortable_str.short_description = "social media"
    _sortable_str.admin_order_field = "handle"

    def _get_artist(self, obj):
        return str(obj.artist_profile.artist)
    _get_artist.short_description = "artist"
    _get_artist.admin_order_field = "artist_profile__artist__name"


@admin.register(Friendship)
class FriendshipAdmin(admin.ModelAdmin):
    pass

