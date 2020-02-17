"""
Created: 17 Feb. 2020
Author: Jordan Prechac
"""

from content.models import Tag


# -----------------------------------------------------------------------------

def get_tag(text, *args, **kwargs):
    """
    Retrieves a tag, or creates one and returns that
    """
    try:
        tag = Tag.objects.get(text=text)
    except Tag.DoesNotExist:
        tag = Tag.objects.create(text=text)
    
    return tag
