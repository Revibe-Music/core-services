"""
Created 14 May 2020
Author: Jordan Prechac
"""

from revibe._errors import network

# -----------------------------------------------------------------------------

class AccountsAPIException(network.APIException):
    default_code = network.status.HTTP_500_INTERNAL_SERVER_ERROR
