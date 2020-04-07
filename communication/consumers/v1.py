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

        # check if users are friends, or allow random messages

        chat = await self.get_chat(user, other_username)
        self.chat = chat

        # add self to channel layer group
        await self.channel_layer.group_add(
            chat.group_name,
            self.channel_name
        )

        # tell the client that the connection has been accepted
        await self.send({
            "type": "websocket.send",
            "text": "Hello, World"
        })

    async def websocket_receive(self, event):
        print("received", event)
        message_body = json.loads(event.get('text', None))

        # echo the message
        await self.send({
            "type": "websocket.send",
            "text": message_body
        })

        # send message to the group
        await self.channel_layer.group_send(
            self.chat.group_name,
            {
                "type": "chat.receive",
                "text": message_body
            }
        )

    async def chat_receive(self, event):
        """
        Received message from the group, send that message to the clients
        """
        print("messaged", event)
        message_body = json.loads(event.get('text', None))

        # send the message to the clients
        await self.send({
            "type": "websocket.send",
            "text": message_body
        })

    async def websocket_disconnect(self, event):
        print("disconnected", event)

        # leave the group
        self.channel_layer.group_discard(
            self.chat.group_name,
            self.channel_name
        )

        await self.send({
            "type": "websocket.close"
        })

    @database_sync_to_async
    def get_chat(self, user, other_username):
        return Chat.objects.get_or_new(user, other_username)

