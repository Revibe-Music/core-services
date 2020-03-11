"""
Created 11 Mar. 2020
Author: Jordan Prechac
"""

from django.db import connection

import gc
import threading

# -----------------------------------------------------------------------------


def perform_async_request(function, *args, **kwargs):
    """
    Wrapper for performing asyncronous functions

    Will automatically close connections and collect garbage before closing the thread
    """
    def call_function(function, *args, **kwargs):
        result = function(*args, **kwargs)

        gc.collect()
        connection.close()

    args = [function] + [arg for arg in args]
    thread = threading.Thread(target=call_function, args=args, kwargs=kwargs)
    thread.setDaemon(True)
    thread.start()

