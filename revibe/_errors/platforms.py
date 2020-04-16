from rest_framework.exceptions import APIException

from revibe._errors import network
from revibe._helpers import const, status

# -----------------------------------------------------------------------------

class InvalidPlatformContent(network.ProgramError):
    default_detail = "Invalid platform content"

class InvalidPlatformOperation(Exception):
    pass

class PlatformNotFoundError(network.BadRequestError):
    default_detail = "The requested platform does not exist"