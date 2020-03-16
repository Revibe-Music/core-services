"""
Created: 16 Mar. 2020
Author: Jordan Prechac
"""

from administration.models import Variable

# -----------------------------------------------------------------------------

def retrieve_variable(variable, default):
    try:
        var = Variable.objects.get(key=variable)
        return var.value
    except Variable.DoesNotExist as dne:
        return default
