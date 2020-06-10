"""
Created: 10 June 2020
"""

from django import forms

from content.models import Image

# -----------------------------------------------------------------------------


class ArtistOfTheWeekImageInlineForm(forms.ModelForm):
    class Meta:
        model = Image
        fields = [
            'artistoftheweek',
            'file',
            'height',
            'width',
        ]

