"""
Created: 22 May 2020
Author: Jordan Prechac
"""

from django.contrib import admin

from administration.models import Blog
from content.models import Image

from . import forms

# -----------------------------------------------------------------------------

class BlogTagInline(admin.TabularInline):
    model = Blog.tags.through

    extra = 1

    verbose_name = "Tag"
    verbose_name_plural = "Tags"


class BlogArtistsInline(admin.TabularInline):
    model = Blog.artists.through

    extra = 1

    verbose_name = "Artist"
    verbose_name_plural = "Artists"


class ArtistOfTheWeekImageInline(admin.TabularInline):
    model = Image
    form = forms.ArtistOfTheWeekImageInlineForm

    extra = 0

    verbose_name = "Image"
    verbose_name_plural = "Images"


