"""
Created 28 May 2020
Author: Jordan Prechac
"""

from accounts.models import CustomUser

from .sorter import Sorter

# -----------------------------------------------------------------------------


def send_weekly_email(run_async=False):
    # split artists from listeners
    available_users = CustomUser.objects.filter(temporary_account=False, programmatic_account=False, profile__allow_email_reminders=True, profile__allow_email_notifications=True)
    artists   = available_users.filter(artist__isnull=False)
    listeners = available_users.filter(artist__isnull=True)

    # send the artist emails
    for artist in artists:
        sorter = Sorter(artist, is_artist=True, run_async=run_async)
        sorter.send_notification()

    # send the listener emails
    for listener in listeners:
        sorter = Sorter(listener, run_async=run_async)
        sorter.send_notification()


