"""
Created: 26 May 2020
Author: Jordan Prechac
"""

# -----------------------------------------------------------------------------

def generate_search_field_text(obj, *args, **kwargs):
    """
    Creates search field text from a search object
    """
    things = (obj.field, obj.type)

    text = "__".join(things)

    return text


