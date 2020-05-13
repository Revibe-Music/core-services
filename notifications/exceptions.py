"""
Created: 13 May 2020
Author: Jordan Prechac
"""

from revibe.exceptions import RevibeException

# -----------------------------------------------------------------------------

class BaseNotificationException(RevibeException):
    pass

class NotificationException(BaseNotificationException):
    pass
