from django.contrib import admin

from surveys.models import *

# -----------------------------------------------------------------------------


@admin.register(ArtistOfTheWeek)
class ArtistOfTheWeekAdmin(admin.ModelAdmin):
    fieldsets = (
        (None, {
            "fields": ('user', 'promotion_ideas', 'picture',),
            "classes": ('extrapretty', 'wide',),
        }),
        ("Social Media", {
            "fields": ('facebook_link', 'instagram_handle', 'soundcloud_link', 'spotify_link', 'youtube_link', ('other_link_description_1', 'other_link_1'),('other_link_description_2', 'other_link_2'),('other_link_description_3', 'other_link_3'),),
            "classes": ('extrapretty', 'wide',),
        }),
        ("Staff Info", {
            "fields": ('seen', 'status', 'staff_notes', 'post',),
            "classes": ('extrapretty', 'wide',),
        }),
        ("Extras", {
            "fields": ('id', 'date_created', 'last_changed',),
            "classes": ('extrapretty', 'wide', 'collapse', 'in',),
        })
    )
    readonly_fields = (
        'id',
        'date_created', 'last_changed',
    )




