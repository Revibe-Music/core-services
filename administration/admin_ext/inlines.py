"""
Created: 22 May 2020
Author: Jordan Prechac
"""

from django.contrib import admin

from administration.models import Blog

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
