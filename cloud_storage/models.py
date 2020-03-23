"""
Created: 23 Mar. 2020
Author: Jordan Prechac
"""

from django.db import models
from django.utils.translation import gettext_lazy as _

from revibe.utils.classes import default_repr

# -----------------------------------------------------------------------------


class File(models.Model):

    _type_choices = (
        ('audio', 'Audio'),
        ('image', 'Image'),
        ('other', 'Other'),
    )

    file = models.FileField(
        null=False, blank=False,
        verbose_name=_("file"),
        help_text=_("The file's file")
    )
    display_name = models.CharField(
        max_length=255,
        null=True, blank=True,
        verbose_name=_("display name"),
        help_text=_("File display name")
    )
    file_type = models.CharField(
        max_length=100,
        choices=_type_choices,
        null=True, blank=True,
        verbose_name=_("file type"),
        help_text=_("The kind of file this is. Helps with filtering and sorting. Not required.")
    )

    owner = models.ForeignKey(
        to='content.Artist',
        on_delete=models.CASCADE,
        related_name="files",
        limit_choices_to={"platform": "Revibe"},
        null=False, blank=False,
        verbose_name=_("owner"),
        help_text=_("The artist that uploaded and owns this file")
    )
    shared_with = models.ManyToManyField(
        to='content.artist',
        related_name='shared_files',
        through='cloud_storage.fileshare',
        verbose_name=_("shared with"),
        help_text=_("Artists that have edit access to the file")
    )

    created_date = models.DateTimeField(
        auto_now_add=True
    )
    last_changed = models.DateTimeField(
        auto_now=True
    )

    def __str__(self):
        if self.display_name not in [None, "", " "]:
            return self.display_name
        return self.file.name

    def __repr__(self):
        return default_repr(self)

    class Meta:
        verbose_name = "file"
        verbose_name_plural = "files"    


class FileShare(models.Model):

    file = models.ForeignKey(
        to='cloud_storage.file',
        on_delete=models.CASCADE,
        related_name='file_shares',
        null=False, blank=False,
        verbose_name=_("file"),
        help_text=_("The related File object")
    )
    artist = models.ForeignKey(
        to='content.artist',
        on_delete=models.CASCADE,
        related_name='file_shares',
        null=False, blank=False,
        verbose_name=_("artist"),
        help_text=_("The Artist the file is shared with")
    )

    date_created = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return str(self.file)
    
    def __repr__(self):
        return default_repr(self)
    
    class Meta:
        verbose_name = "shared file"
        verbose_name_plural = "shared files"
