"""
Created: 9 Mar. 2020
Author: Jordan Prechac
"""

from rest_framework.serializers import ListSerializer

# -----------------------------------------------------------------------------


class ProcessedOnlyListSerializer(ListSerializer):

    def to_representation(self, data):
        data = data.filter(is_original=False)
        return super().to_representation(data)
