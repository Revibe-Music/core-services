"""
Created: 16 Mar. 2020
Author: Jordan Prechac
"""

from revibe._errors.network import BadRequestError

from administration.models import Alert

# -----------------------------------------------------------------------------

def see_alert(user, alert):
    try:
        user.alerts_seen.add(alert)
    except Exception as e:
        raise BadRequestError(f"Could not record seeing alert. Error: {e}")
