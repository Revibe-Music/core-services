"""
Created: 06 Feb. 2020
Author: Jordan Prechac
"""

# imports

# -----------------------------------------------------------------------------

def get_url_param(params, var, *args, **kwargs):
    """
    Wrapper for getting a variable from a url parameter. 

    Necessary because url params can be registered as lists, so this will get a single value if it can be found
    """
    param = params.get(var, None)
    if param == None:
        return None

    if type(param) == list:
        if len(param) > 1:
            return param
        else:
            param = param[0]
    
    return param


def convert_param_to_bool(params, var, default=None, *args, **kwargs):
    """
    Gets a parameter that should be a bool and gets the boolean from it

    Ex.: can get bool from True, TRUE, tRuE, or 1
    """
    # validate arguments
    if default != None:
        assert bool(default) in [True, False], "Argument 'default' must be either True or False"

    # get the parameter
    param = get_url_param(params, var, *args, **kwargs)
    if param == None:
        return default if default != None else False
    elif isinstance(param, list):
        return True
    
    # check if it's a numeric value
    if isinstance(param, int):
        return bool(param)
    
    # convert strings to bool
    if isinstance(param, str):
        param = param.lower()
        if param in ['true', 't']:
            return True
        elif param in ['false', 'f']:
            return False
    
    # if nothing has been returned yet, send default or nothing
    if default != None:
        return bool(default)
    else:
        return None
