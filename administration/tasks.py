"""
Register Celery tasks

Created: 01 Jun, 2020
Author: Jordan Prechac
"""

from celery import shared_task

# from .utils.cleaner import Cleaner

# -----------------------------------------------------------------------------

@shared_task
def backend_cleanup(detail=False):
    from administration.utils.cleaner import Cleaner

    cleaner = Cleaner()
    return cleaner.clean(detail=detail)
