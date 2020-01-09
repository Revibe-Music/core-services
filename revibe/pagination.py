from rest_framework.pagination import LimitOffsetPagination

from logging import getLogger
logger = getLogger(__name__)

from revibe._helpers import const

# -----------------------------------------------------------------------------


class NestedLimitOffsetPagination(LimitOffsetPagination):
    """
    DEPRECATED
    Custom LimitOffset Pagination class
    for our own stuff.

    We need to be able to paginate lists that are a part of the request, not
    just lists that are the request.
    """
    default_limit = const.PAGINATION_SIZE
    max_limit = const.MAX_PAGINATION_SIZE

    def paginate_queryset(self, queryset, request, view=None):
        self.count = self.get_count(queryset)
        self.limit = self.get_limit(request) # returns limit in request or default limit, all maxed to set max
        if self.limit is None:
            return None

        self.offset = self.get_offset(request)
        self.request = request
        if self.count > self.limit and self.template is not None:
            self.display_page_controls = True

        if self.count == 0 or self.offset > self.count:
            return []
        return list(queryset[self.offset:self.offset + self.limit])

    def get_paginated_response(self, data):
        return Response(OrderedDict([
            ('count', self.count),
            ('next', self.get_next_link()),
            ('previous', self.get_previous_link()),
            ('results', data)
        ]))
