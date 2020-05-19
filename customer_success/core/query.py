"""
"""

from django.db.models import Q

import datetime

from accounts.models import CustomUser

# -----------------------------------------------------------------------------

def group_users(group, ids=False):
    """
    Returns a list of users.

    With 'group' = 'active':
        Returns users that have registered over 2 weeks ago, are not temporary,
            and have logged in to the service in the last week.
    
    With 'group' = 'inactive':
        Returns users that have registered over 2 weeks ago, are not temporary,
            and have not logged in to the service in the last week.
    
    With 'group' = 'new':
        Returns users that registered within the last 2 weeks.
    """

    assert group in ['active', 'inactive', 'new']

    now = datetime.datetime.now()
    one_week  = now - datetime.timedelta(days=7)
    two_weeks = now - datetime.timedelta(days=14)

    if group == 'active':
        flter = Q(
            date_joined__lte=two_weeks,
            last_login__gte=one_week
        )
    elif group == 'inactive':
        flter = Q(
            Q(last_login__lte=one_week) | Q(last_login__isnull=True),
            date_joined__lte=two_weeks,
        )
    else: # group == 'new'
        flter = Q(
            date_joined__gte=two_weeks
        )

    users = CustomUser.registered_objects.filter(flter)

    if ids: # only return the ID's of the users
        ids = users.values_list('id')
        return [id[0] for id in ids]

    return users

