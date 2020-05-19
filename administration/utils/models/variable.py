"""
Created: 16 Mar. 2020
Author: Jordan Prechac
"""

from administration.models import Variable

# -----------------------------------------------------------------------------

def retrieve_variable(variable, default, is_bool=False, output_type=None):
    try:
        var = Variable.objects.get(key=variable)
        value = var.value
    except Variable.DoesNotExist as dne:
        return default
    except Exception:
        return default

    # look for boolean values if the output should be a boolean
    if is_bool or output_type==bool:
        if value in ('False', 'false', False, 0):
            value = False
        elif value in ('True', 'true', True, 1):
            value = True
        else:
            value = default

    elif output_type != None:
        try:
            return output_type(value)
        except Exception:
            pass

    return value
