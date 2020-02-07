from django.contrib import admin
from .models import *

# -----------------------------------------------------------------------------

# Register your models here.

@admin.register(CustomUser)
class CustomUserAdmin(admin.ModelAdmin):
    # customize list display
    list_display = ('__str__', '_full_name', 'date_joined')
    list_filter = (
        ('date_joined', admin.DateFieldListFilter),
        ('is_staff', admin.BooleanFieldListFilter),
    )

    # customize search
    search_fields = ['username', 'first_name', 'last_name']

    # customize actions
    # actions = [change_password]

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
    search_fields = ['artist', 'email',]

    def get_artist_username(self, obj):
        return obj.artist.artist_user.username
    get_artist_username.short_description = 'username'

