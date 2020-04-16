"""
Created: 16 Apr. 2020
Author: Jordan Prechac
"""

from .base import *

# -----------------------------------------------------------------------------

__all__ = [
    # 1xx
    # 2xx
    AlreadyReportedError,
    # 3xx
    # 4xx
    BadRequestError, UnauthorizedError, ForbiddenError, NotFoundError,
    ConflictError, ExpectationFailedError,
    # 5xx
    NotImplementedError, ServiceUnavailableError, ProgramError,
    PageUnavailableError,
]
