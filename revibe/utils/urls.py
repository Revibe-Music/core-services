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

