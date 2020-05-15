"""
Created 14 May 2020
Author: Jordan Prechac
"""

from revibe._errors import network

# -----------------------------------------------------------------------------

class AccountsAPIException(network.APIException):
    status_code = network.status.HTTP_500_INTERNAL_SERVER_ERROR

class AccountsBadRequestError(
        network.BadRequestError,
        AccountsAPIException
    ):
    pass

class AccountsConflicError(
        network.ConflictError,
        AccountsAPIException
    ):
    pass
