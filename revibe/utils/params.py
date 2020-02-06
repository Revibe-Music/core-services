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
