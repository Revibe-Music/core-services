"""
Created: 06 Apr. 2020
Author: Jordan Prechac
"""

from django.conf.urls import url
from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.security.websocket import AllowedHostsOriginValidator, OriginValidator

from communication.consumers.v1 import ChatConsumer

# -----------------------------------------------------------------------------

application = ProtocolTypeRouter({
    # empty for now
    'websocket': AllowedHostsOriginValidator(
        AuthMiddlewareStack(
            URLRouter(
                [
                    url(r"v1/communication/chat/^(?P<username>[/w.@+-])/?", ChatConsumer) # ws://api.revibe.tech/v1/communication/chat/<username>/
                ]
            )
        )
    )
})
