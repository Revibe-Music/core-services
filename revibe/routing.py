"""
Created: 06 Apr. 2020
Author: Jordan Prechac
"""

from django.conf.urls import url
from django.urls import re_path
from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.security.websocket import AllowedHostsOriginValidator, OriginValidator

import asyncio

from revibe.middleware.channels import ChannelsTokenAuthMiddleware

# from communication.consumers.v1 import ChatConsumer
import communication.routing.v1

# -----------------------------------------------------------------------------

application = ProtocolTypeRouter({
    # empty for now
    'websocket': AllowedHostsOriginValidator(
        ChannelsTokenAuthMiddleware(
            URLRouter(
                communication.routing.v1.wesocket_urlpatterns
            )
        )
    )
})
