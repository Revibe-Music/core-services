"""
Created: 07 Apr. 2020
Author: Jordan Prechac
"""

from django.db import close_old_connections
from channels.middleware import BaseMiddleware

# -----------------------------------------------------------------------------

class ChannelsTokenAuthMiddleware(BaseMiddleware):
    def populate_scope(self, scope):
        print("Scope populated!", scope)
    
    async def resolve_scope(self, scope):
        print("Scope resolved!", scope)

