"""
Created: 20 Mar. 2020
Author: Jordan Prechac
"""

from django.db.models import IntegerField

# -----------------------------------------------------------------------------


class IntegerRangeField(IntegerField):
    def __init__(self, verbose_name=None, name=None, min_value=None, max_value=None, **kwargs):
        self.min_value, self.max_value = min_value, max_value
        super().__init__(verbose_name, name, **kwargs)
    
    def formfield(self, **kwargs):
        defaults = {'min_value': self.min_value, 'max_value': self.max_value}
        defaults.update(kwargs)
        return super().formfield(**defaults)

