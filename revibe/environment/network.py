import socket

from logging import getLogger
logger = getLogger(__name__)

# -----------------------------------------------------------------------------

def getHostIP():
    try:
        host_name = socket.gethostname()
        host_ip = socket.gethostbyname(host_name)
    except Exception as e:
        logger.error("Could not retrieve host name and/or IP.")
        logger.error(str(e))
    finally:
        logger.info(f"Host Name: {host_name}")
        logger.info(f"Host IP: {host_ip}")
        return host_ip
