"""
Created: 20 Mar. 2020
Author: Jordan Prechac
"""

from django.db import models
from django.db.models import F
from django.db.models.expressions import ExpressionWrapper

from marketplace.utils.models.good import discounted_price

# -----------------------------------------------------------------------------

class GoodObjectsManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset() \
            .annotate(
                discounted_price = ExpressionWrapper(discounted_price(F('price'), F('discount')), output_field=models.DecimalField())
            )
