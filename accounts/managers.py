"""
"""

from django.contrib.auth.models import BaseUserManager

# -----------------------------------------------------------------------------

class RegisteredUserManager(BaseUserManager):
    def get_queryset(self):
        return super().get_queryset().filter(
            programmatic_account=False,
            temporary_account=False
        )
