"""
Created: 20 May 2020
Author: Jordan Prechac
"""

from django import forms

from customer_success.models import PathwayAction

# -----------------------------------------------------------------------------

class PathwayActionInlineForm(forms.ModelForm):
    class Meta:
        model = PathwayAction
        fields = [
            'pathway',
            'action',
            'ranking',
            'active',
        ]


