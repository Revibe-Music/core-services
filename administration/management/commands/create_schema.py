from django.core.management.base import BaseCommand
from django.conf import settings

import MySQLdb
import os

# -----------------------------------------------------------------------------

class Command(BaseCommand):

    def handle(self, *args, **kwargs):
        if (not settings.DEBUG) and (settings.USE_S3):
            db = MySQLdb.connect(
                host=os.environ['RDS_WRITE_HOSTNAME'],
                user=os.environ['RDS_USERNAME'],
                password=os.environ['RDS_PASSWORD']
            )

            cur = db.cursor()

            cur.execute(f"CREATE SCHEMA {os.environ['RDS_DB_NAME']}")
        else:
            pass
