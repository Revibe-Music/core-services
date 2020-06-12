"""
Created: 12 June 2020
"""

from django.conf import settings
from django.core.mail import send_mail

import datetime

from administration.utils import retrieve_variable

# -----------------------------------------------------------------------------

ERROR_EMAIL_SUBJECT = 'Email Logger'
ERROR_FROM_EMAIL = '"Revibe Email Logger" <noreply@revibe.tech>'
ERROR_EMAIL_FAIL_SILENTLY = True

def _error_email(to, func_name, exc):
    # only allow email logging to '@revibe.tech' email address
    if '@revibe.tech' not in to: raise ValueError("Can only log messages via email to @revibe.tech email addresses")

    # convert recipients to list
    recipients = [to,]

    # configure the message
    message = f"Function '{func_name}' " + \
        f"raised exception: {exc}" + \
        f"\nTimestamp: {datetime.datetime.now()}" + \
        f"\nEnvironment: {settings.ENV}"

    # send the email
    send_mail(
        subject=ERROR_EMAIL_SUBJECT,
        from_email=ERROR_FROM_EMAIL,
        message=message,
        recipient_list=recipients,
        fail_silently=ERROR_EMAIL_FAIL_SILENTLY
    )

def error_email(to, func_name, exc, raise_exception=True):
    """
    """
    try:
        return _error_email(to, func_name, exc)
    except Exception as e:
        if raise_exception: raise e
        return


