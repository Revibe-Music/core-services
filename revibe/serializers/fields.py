"""
Created: 19 Feb. 2020
Author: Jordan Prechac
"""
from rest_framework.serializers import DateField

import datetime

# -----------------------------------------------------------------------------

class CustomDateField(DateField):
    def to_representation(self, value):
        if isinstance(value, datetime.datetime):
            value = value.date()
        return super().to_representation(value)
