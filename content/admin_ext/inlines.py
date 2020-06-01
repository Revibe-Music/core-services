"""
Created: 22 May 2020
Author: Jordan Prechac
"""

from django.contrib import admin

from content.admin_ext.forms import AlbumContributorInlineForm, SongContributorInlineForm
from content.models import Album, AlbumContributor, Song, SongContributor, Track

# -----------------------------------------------------------------------------

class AlbumContributorInline(admin.TabularInline):
    model = AlbumContributor
    form = AlbumContributorInlineForm

    extra = 1

    verbose_name = "contributor"
    verbose_name_plural = "contributors"


class AlbumGenreInline(admin.TabularInline):
    model = Album.genres.through

    extra = 1

    verbose_name = "genre"
    verbose_name_plural = "genres"


class AlbumTagInline(admin.TabularInline):
    model = Album.tags.through

    extra = 1

    verbose_name = "tag"
    verbose_name_plural = "tags"


class SongContributorInline(admin.TabularInline):
    model = SongContributor
    form = SongContributorInlineForm

    extra = 1

    verbose_name = "contributor"
    verbose_name_plural = "contributors"


class SongGenreInline(admin.TabularInline):
    model = Song.genres.through

    extra = 1

    verbose_name = "genre"
    verbose_name_plural = "genres"


class SongTagInline(admin.TabularInline):
    model = Song.tags.through

    extra = 1

    verbose_name = "tag"
    verbose_name_plural = "tags"

class SongTrackInline(admin.TabularInline):
    model = Track

    extra = 1

    verbose_name = "track"
    verbose_name_plural = "tracks"
