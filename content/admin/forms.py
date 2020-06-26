"""
Created: 22 May 2020
Author: Jordan Prechac
"""

from django import forms

from content.models import Album, AlbumContributor, Artist, Song, SongContributor

# -----------------------------------------------------------------------------

_contributor_choices = (
    ('Artist', 'Artist'),
    ('Feature', 'Feature'),
    ('Producer', 'Producer'),
    ('Mixing', 'Mixing'),
    ('Mastering', 'Mastering'),
    ('Song Writer', 'Song Writer'),
    ('Vocals', 'Vocals'),
    ('Programmer/Beat Maker', 'Programmer/Beat Maker'),
    ('Graphic Designer', 'Graphic Designer')
)

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
        widgets = {
            "contribution_type": forms.Select(choices=_contributor_choices)
        }


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
        widgets = {
            "contribution_type": forms.Select(choices=_contributor_choices)
        }

_platform_choices = (
    ('Revibe', 'Revibe'),
    ('Spotify', 'Spotify'),
    ('YouTube', 'Youtube'),
)
class AlbumAdminForm(forms.ModelForm):
    class Meta:
        model = Album
        fields = '__all__'
        widgets = {
            "platform": forms.Select(choices=_platform_choices)
        }
class ArtistAdminForm(forms.ModelForm):
    class Meta:
        model = Artist
        fields = '__all__'
        widgets = {
            "platform": forms.Select(choices=_platform_choices)
        }
class SongAdminForm(forms.ModelForm):
    class Meta:
        model = Song
        fields = '__all__'
        widgets = {
            "platform": forms.Select(choices=_platform_choices)
        }

