from rest_framework.exceptions import APIException

from logging import getLogger
logger = getLogger(__name__)

from revibe._errors import network
from revibe._helpers import const, status

# -----------------------------------------------------------------------------

class ParameterMissingError(network.ExpectationFailedError):
    default_detail = "missing paramter, please check the docs for request requirements"


class SerializerValidationError(network.ExpectationFailedError):
    default_detail = "misc. serializer error, please try again"


class TooManyObjectsReturnedError(network.ProgramError):
    default_detail = "Too many objects found, please try again"


class ObjectAlreadyExists(network.AlreadyReportedError):
    default_detail = "The request object already exists"


class NoKeysError(network.BadEnvironmentError):
    default_detail = "Could not find any valid keys"
