"""
Author: Jordan Prechac
Created: 06 Jan, 2020
"""

from urllib import request

from logging import getLogger
logger = getLogger(__name__)

# -----------------------------------------------------------------------------

def getHostIP():
    """
    Gets the IP address of the current host.

    Written to be used in adding the current host to ALLOWED_HOSTS in settings.
    """
    try:
        private_ip = request.urlopen("http://169.254.169.254/latest/meta-data/local-ipv4").read()
    except Exception as e:
        logger.error("Could not retrieve IP address.")
        logger.error(str(e))
        raise e
    else:
        logger.info(f"Host IP: {private_ip}")
        return private_ip
