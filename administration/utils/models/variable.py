"""
Created: 16 Mar. 2020
Author: Jordan Prechac
"""

from django.apps import apps
Variable = apps.get_model('administration', 'Variable')

# -----------------------------------------------------------------------------

def retrieve_variable(variable, default, is_bool=False, output_type=str):
    return Variable.objects.retrieve(variable, default, output_type=output_type)
