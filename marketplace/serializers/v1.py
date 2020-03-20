"""
Created: 20 Mar. 2020
Author: Jordan Prechac
"""

from rest_framework import serializers

from marketplace.models import Good

# -----------------------------------------------------------------------------

class GoodSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Good
        fields = '__all__'
