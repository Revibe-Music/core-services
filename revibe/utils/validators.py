"""
Created: 9 Mar. 2020
Author: Jordan Prechac
"""

from uuid import UUID

# -----------------------------------------------------------------------------

def is_valid_uuid(uuid_to_test, version=4):
    """
    Check if uuid_to_test is a valid UUID.

    Parameters
    ----------
    uuid_to_test : str
    version : {1, 2, 3, 4}

    Returns
    -------
    `True` if uuid_to_test is a valid UUID, otherwise `False`.

    Examples
    --------
    >>> is_valid_uuid('c9bf9e57-1685-4c89-bafb-ff5af830be8a')
    True
    >>> is_valid_uuid('c9bf9e58')
    False
    """
    try:
        uuid_obj = UUID(uuid_to_test, version=version)
    except ValueError:
        return False

    return str(uuid_obj) == uuid_to_test

def is_valid_int(int_to_test):
    """
    Check if int_to_test is a valid integer
    
    Parameters
    ----------
    int_to_test : str

    Returns
    -------
    'True' if int_to_test if a valid int, otherwise 'False'

    Examples
    --------
    >>> is_valid_int('73')
    True
    >>> is_valid_int('5g8vdFp')
    False
    """
    try:
        int_obj = int(int_to_test)
    except ValueError:
        return False
    
    return str(int_obj) == int_to_test

