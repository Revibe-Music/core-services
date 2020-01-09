from rest_framework.pagination import LimitOffsetPagination

from logging import getLogger
logger = getLogger(__name__)

from revibe._helpers import const

# -----------------------------------------------------------------------------


class CustomLimitOffsetPagination(LimitOffsetPagination):
    """
    Custom LimitOffset Pagination class that utilizes our own default and max
    limits.
    """
    default_limit = const.PAGINATION_SIZE
    max_limit = const.MAX_PAGINATION_SIZE
