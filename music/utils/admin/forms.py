"""
Created: 22 May 2020
Author: Jordan Prechac
"""

from django import forms

from music.models import PlaylistSong

# -----------------------------------------------------------------------------


class PlaylistSongInlineForm(forms.ModelForm):
    class Meta:
        model = PlaylistSong
        fields = [
            'playlist',
            'song',
            'order',
        ]


