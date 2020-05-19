"""
"""

from django.db.models import Manager

# -----------------------------------------------------------------------------

class RegisteredUserManager(Manager):
    def get_queryset(self):
        return super().get_queryset().filter(
            programmatic_account=False,
            temporary_account=False
        )
