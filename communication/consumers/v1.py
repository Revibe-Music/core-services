"""
Created: 06 Apr. 2020
Author: Jordan Prechac
"""

from django.contrib.auth import get_user_model
from channels.consumer import AsyncConsumer
from channels.db import database_sync_to_async

import asyncio
import json

from ..models import Chat, Message

# -----------------------------------------------------------------------------

class ChatConsumer(AsyncConsumer):
    # this is based on an example on YouTube (link in the README file)
    # please ignore this functionality, there's not a lot of functionality here anyway

    async def websocket_connect(self, event):
        print("connected", event)

        await self.send({
            "type": "websocket.accept"
        })

        user = self.scope['user']
        other_username = self.scope['url_route']['kwargs']['username']
        chat = await self.get_chat(user, other_username)

        await self.send({
            "type": "websocket.send",
            "text": "Hello, World"
        })

    async def websocket_receive(self, event):
        print("received", event)

    async def websocket_disconnect(self, event):
        print("disconnected", event)

        await self.send({
            "type": "websocket.close"
        })

    @database_sync_to_async
    def get_chat(self, user, other_username):
        return Chat.objects.get_or_new(user, other_username)

