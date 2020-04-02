"""
Created: 16 Mar. 2020
Author: Jordan Prechac
"""

from administration.models import Variable

# -----------------------------------------------------------------------------

def retrieve_variable(variable, default, is_bool=False):
    try:
        var = Variable.objects.get(key=variable)
        value = var.value
    except Variable.DoesNotExist as dne:
        return default
    except Exception:
        return default

    if is_bool:
        if value in ('False', 'false', False):
            value = False
        elif value in ('True', 'true', True):
            value = True
        else:
            value = default

    return value
