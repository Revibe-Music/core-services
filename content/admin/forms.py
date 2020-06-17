"""
Created: 22 May 2020
Author: Jordan Prechac
"""

from django import forms

from content.models import AlbumContributor, Song, SongContributor

# -----------------------------------------------------------------------------

class AlbumContributorInlineForm(forms.ModelForm):
    class Meta:
        model = AlbumContributor
        fields = [
            'album',
            'artist',
            'contribution_type',
            'pending',
            'approved',
            'primary_artist',
        ]


class AlbumSongInlineForm(forms.ModelForm):
    class Meta:
        model = Song
        fields = [
            'title',
            'album_order',
            'is_displayed',
        ]


class SongContributorInlineForm(forms.ModelForm):
    class Meta:
        model = SongContributor
        fields = [
            'song',
            'artist',
            'contribution_type',
            'pending',
            'approved',
            'primary_artist',
        ]

