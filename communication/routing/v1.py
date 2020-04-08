"""
Created: 08 Apr. 2020
Author: Jordan Prechac
"""

from django.conf.urls import url
from django.urls import re_path

import asyncio

from ..consumers.v1 import ChatConsumer

# -----------------------------------------------------------------------------

wesocket_urlpatterns = [
    re_path(r'ws/v1/communication/chat/(?P<username>\w+)/$', ChatConsumer),
]
