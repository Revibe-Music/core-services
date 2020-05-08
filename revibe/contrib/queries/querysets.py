"""
Created: 08 May 2020
Author: Jordan Prechac
"""

from django.db.models import Count

from random import randint

# -----------------------------------------------------------------------------

def random_object(queryset, pk_field='id'):
    count = queryset.aggregate(count=Count(pk_field))['count']
    random_index = randint(0, count - 1)
    return queryset[random_index]
