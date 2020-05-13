"""
Created: 13 May 2020
Author: Jordan Prechac
"""

import logging
logger = logging.getLogger(__name__)

from revibe.utils import getattr_or_get

from accounts.models import CustomUser
from content import models

# -----------------------------------------------------------------------------


def get_album_id(obj):
    if isinstance(obj, dict):
        if 'album_id' in obj.keys():
            return obj.get('album_id')
        elif 'album' in obj.keys():
            return get_album_id(obj.get('album'))

    else:
        if hasattr(obj, 'album_id'):
            return getattr(obj, 'album_id')
        
        elif hasattr(obj, 'album'):
            return get_album_id(getattr(obj, 'album'))
    
    return None


def get_song_id(obj):
    if isinstance(obj, dict):
        if 'song_id' in obj.keys():
            return obj.get('song_id')
        elif 'song' in obj.keys():
            return get_song_id(obj.get('song'))

    else:
        if hasattr(obj, 'song_id'):
            return getattr(obj, 'song_id')
        
        elif hasattr(obj, 'song'):
            return get_song_id(getattr(obj, 'song'))

    return None


def take_step(obj, step):
    """ Takes a step towards a target obj """
    temp_obj = getattr_or_get(obj, step)

    if 'id' in step:
        # if the step is an ID, we need to get the object represented by that id
        model_str = step.split('_')[0].lower().capitalize()
        if model_str != 'User':
            model = getattr_or_get(models, model_str, None)
            if model == None:
                logger.warn(f"Could not find model '{model_str}' in the take_step() method")
                return None
        else:
            model = CustomUser

        try:
            obj = model.objects.get(id=temp_obj)
            return obj
        except model.DoesNotExist as e:
            logger.warn(str(e))
    return temp_obj





