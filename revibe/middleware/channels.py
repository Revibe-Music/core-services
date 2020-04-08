"""
Created: 07 Apr. 2020
Author: Jordan Prechac
"""

from django.db import close_old_connections
from channels.db import database_sync_to_async
from channels.middleware import BaseMiddleware
from oauth2_provider.models import AccessToken

import asyncio

from revibe.utils.urls import split_query_params
from revibe._errors.auth import NoAuthenticationError

# -----------------------------------------------------------------------------

@database_sync_to_async
def get_user_from_access_token(token):
    try:
        user = AccessToken.objects.get(token=token).user
    except AccessToken.DoesNotExist:
        raise NoAuthenticationError("Could not verify access token")

    return user

# class ChannelsTokenAuthMiddleware(BaseMiddleware):
#     def populate_scope(self, scope):
#         # this is where we do the authenticating
#         print("Scope populated!")

#         if "user" not in scope:
#             # url query parameters are located in scope.query_string
#             params_bytes = scope['query_string']
#             params_string = params_bytes.decode("utf-8")

#             params = split_query_params(params_string)

#             auth_token = params.get('authorization', None)
#             if auth_token == None:
#                 raise NoAuthenticationError()

#             user = self.get_user_from_access_token(auth_token)
#             print(user)

#             scope["user"] = user

#     async def resolve_scope(self, scope):
#         print("Scope resolved!")
#         scope["user"]._wrapped = scope.get('user', None)


class ChannelsTokenAuthMiddleware:
    def __init__(self, inner):
        self.inner = inner
        
    def __call__(self, scope):
        return ChannelsTokenAuthMiddlewareInstance(scope, self)

        # must do this cause docs: https://channels.readthedocs.io/en/latest/topics/authentication.html
        close_old_connections()

        

class ChannelsTokenAuthMiddlewareInstance:
    def __init__(self, scope, middleware):
        self.middleware = middleware
        self.scope = dict(scope)
        self.inner = self.middleware.inner
    
    async def __call__(self, receive, send):
        # get the user
        if "user" not in self.scope:
            # url query parameters are located in scope.query_string
            params_bytes = self.scope['query_string']
            params_string = params_bytes.decode("utf-8")

            params = split_query_params(params_string)

            auth_token = params.get('authorization', None)
            if auth_token == None:
                raise NoAuthenticationError()

            self.scope["user"] = await get_user_from_access_token(auth_token)

        inner = self.inner(self.scope)
        return await inner(receive, send)

