from django.core.management.base import BaseCommand
from django.conf import settings

from logging import getLogger
logger = getLogger(__name__)

from revibe.environment import network

# -----------------------------------------------------------------------------

class Command(BaseCommand):

    def handle(self, *args, **kwargs):
        pass
        # if (not settings.DEBUG) and (settings.USE_S3):
        #     ip = network.getHostIP()
        #     s = f"Host IP Address: {ip}"
        #     print(s)
        #     logger.info(s)
        #     self.stdout.write(s)
