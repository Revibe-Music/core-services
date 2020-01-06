"""
Author: Jordan Prechac
Created: 06 Jan, 2020
"""

import socket

from logging import getLogger
logger = getLogger(__name__)

# -----------------------------------------------------------------------------

def getHostIP():
    """
    Gets the IP address of the current host.

    Written to be used in adding the current host to ALLOWED_HOSTS in settings.
    """
    try:
        host_name = socket.gethostname()
        host_ip = socket.gethostbyname(host_name)
    except Exception as e:
        logger.error("Could not retrieve host name and/or IP.")
        logger.error(str(e))
        raise e
    else:
        logger.info(f"Host Name: {host_name}")
        logger.info(f"Host IP: {host_ip}")
        return host_ip
