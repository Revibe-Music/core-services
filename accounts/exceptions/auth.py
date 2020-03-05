"""
Created: 5 Mar. 2020
Author: Jordan Prechac
"""

from rest_framework.exceptions import APIException

from revibe._errors.network import ExpectationFailedError

# -----------------------------------------------------------------------------

class PasswordValidationError(ExpectationFailedError):
    default_detail = "Password did not meet password validation"
