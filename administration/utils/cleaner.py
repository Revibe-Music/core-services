"""
Class that runs a series of cleanup functions on the database.

Created: 01 Jun, 2020
Author: Jordan Prechac
"""

from django.db.models import Case, F, Q, Value, When

from accounts.models import CustomUser
from administration.models import Variable

# -----------------------------------------------------------------------------

class Cleaner:

    def __init__(self, *args, **kwargs):

        self.vars = Variable.objects.filter(active=True, category=Variable.CLEANUP)

        self.args = args
        self.kwargs = kwargs

        self.force_var_update = False

    @property
    def funcs(self):
        funcs = []
        for var in self.vars:
            func_name = var.key.replace('-','_')
            if hasattr(self, func_name):
                funcs.append(getattr(self, func_name))

        return funcs

    def adjust_user_is_artist_bool(self):
        # get the users that may be an artist, but are not correctly listed
        adjusting_users = CustomUser.objects.filter(
            Q(artist__isnull=False) | Q(is_artist=True),
            is_active=True,
            programmatic_account=False,
            temporary_account=False
        ).exclude(
            artist__isnull=False,
            is_artist=True
        )

        num_users = adjusting_users.count()

        adjusting_users.update(is_artist=Case(
            When(artist__isnull=False, then=Value(True)), # There IS an artist listed
            default=Value(False)
        ))

        return num_users

    def clean(self, detail=False):
        output = {}
        errs = {}
        for func in self.funcs:
            try:
                o = func()
            except Exception as e:
                errs.update({func.__name__: str(e)})
            else:
                output.update({func.__name__: o})

        if detail:
            return output, errs
        else:
            return len(output), len(errs)


