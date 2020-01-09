from rest_framework.exceptions import APIException

from logging import getLogger
logger = getLogger(__name__)

from revibe._errors import network
from revibe._helpers import const, status

# -----------------------------------------------------------------------------

class ParameterMissingError(network.ExpectationFailedError):
    default_detail = "missing paramter, please check the docs for request requirements"
