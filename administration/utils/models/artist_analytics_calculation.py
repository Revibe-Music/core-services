"""
Created: 04 May 2020
Author: Jordan Prechac
"""

from administration.models import ArtistAnalyticsCalculation

# -----------------------------------------------------------------------------

def retrieve_calculation(calculation_name, default=None):
    try:
        calc = ArtistAnalyticsCalculation.objects.get(name=calculation_name)
    except ArtistAnalyticsCalculation.DoesNotExist as dne:
        return default
    except Exception as e:
        return default
    
    return calc

