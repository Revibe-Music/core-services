"""
"""

from notifications.models import Event

# -----------------------------------------------------------------------------

def get_event(events=None, raise_exception=False, *args, **kwargs):
    try:
        if events:
            # the function was sent an event queryset
            return events.get(*args, **kwargs)
        else:
            return Event.active_objects.get(*args, **kwargs)

    except Event.DoesNotExist as e:
        if raise_exception:
            raise e
        else:
            return None


def get_events(events=None, *args, **kwargs):
    if events:
        return events.filter(*args, **kwargs)
    else:
        return Event.active_objects.filter(*args, **kwargs)
