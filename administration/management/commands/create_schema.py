from django.core.management.base import BaseCommand

import MySQLdb
import os

# -----------------------------------------------------------------------------

class Command(BaseCommand):

    def handle(self, *args, **kwargs):
        db = MySQLdb.connect(
            host=os.environ['RDS_WRITE_HOSTNAME'],
            user=os.environ['RDS_USERNAME'],
            password=os.environ['RDS_PASSWORD']
        )

        cur = db.cursor()

        cur.execute(f"CREATE SCHEMA {os.environ['RDS_DB_NAME']}")
