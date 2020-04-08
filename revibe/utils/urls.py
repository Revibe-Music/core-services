"""
Created: 9 Mar. 2020
Author: Jordan Prechac
"""

from revibe.utils.validators import is_valid_uuid, is_valid_int

# -----------------------------------------------------------------------------

def replace_url_id(url):
    """
    Takes a url and replaces aspects of it with <id>
    if any part of the url is an ID - UUID or int
    """

    sep_char = '/'

    components = url.split(sep_char)
    id_string = "<id>"

    for comp in components:
        if is_valid_uuid(comp) or is_valid_int(comp):
            components[components.index(comp)] = id_string

    return sep_char.join(components)


def add_query_params(url, params):
    """
    Takes a string url and a dictionary of parameters and generates a url.

    Arguments
    ---------
    url: (str) the base url
    params: (dict) the url parameters to add to it

    Examples
    --------
    >>> add_query_params("api.revibe.tech", {"uid": 2})
    "api.revibe.tech?uid=2
    
    >>> add_query_params("api.revibe.tech", {"uid": 2, "cid": "49gb2"})
    "api.revibe.tech?uid=2&cid=49gb2"
    """
    if url[-1] != "?":
        url += "?"

    param_string = "&".join([f"{key}={value}" for key, value in params.items()])

    return url + param_string


def split_query_params(url, full=False):
    """
    Returns a dict of stuff
    """
    output = {}

    if full:
        param_string = url.split('?')[1] # get only the end of the url
    else:
        param_string = url

    params = param_string.split('&')
    for param in params:
        thing = param.split('=')
        output.update({thing[0]: thing[1]})

    return output

