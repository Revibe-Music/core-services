"""
Created: 07 Apr. 2020
Author: Jordan Prechac
"""

from django.db import models
from django.db.models import Q

from revibe._errors import network

# -----------------------------------------------------------------------------

class ChatManager(models.Manager):
    def get_or_new(self, user, other_username):
        username = user.username

        if username == other_username:
            return None
        
        qlookup1 = Q(first__username=username) & Q(second__username=other_username)
        qlookup2 = Q(first__username=other_username) & Q(second__username=username)
        qs = self.get_queryset().filter(qlookup1 | qlookup2).distinct()

        if qs.count() == 1:
            return qs.first()
        elif qs.count() > 1:
            return qs.order_by('created').first(), False
        else:
            Klass = user.__class__

            try:
                user2 = Klass.objects.get(username=other_username)
            except Klass.DoesNotExist:
                raise network.BadRequestError(f"Could not find a user with username '{other_username}'")

            if user != user2:
                obj = self.model(
                    first=user,
                    second=user2
                )
                obj.save()
                return obj
            return None

