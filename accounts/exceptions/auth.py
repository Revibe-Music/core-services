"""
Created: 5 Mar. 2020
Author: Jordan Prechac
"""

from .base import AccountsException

# -----------------------------------------------------------------------------


class PasswordValidationError(AccountsException):
    pass

class AuthError(AccountsException):
    pass

