"""
Created 21 May 2020
Author: Jordan Prechac
"""

from revibe.exceptions import RevibeException

# -----------------------------------------------------------------------------

class BaseCustomerSuccessException(RevibeException):
    pass

class CustomerSuccessException(BaseCustomerSuccessException):
    pass
