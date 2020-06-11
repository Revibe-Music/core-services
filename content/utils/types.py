"""
Created: 11 June 2020
"""

import json

# -----------------------------------------------------------------------------


def _validate_list(lst, raise_exception: bool=False):
    if isinstance(lst, (list, tuple)):
        return list(lst)

    try:
        lst = json.loads(lst)
    except json.JSONDecodeError as e:
        if raise_exception:
            raise e
        else:
            return

    return lst
