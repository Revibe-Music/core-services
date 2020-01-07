import random

from revibe._helpers import const

# -----------------------------------------------------------------------------

class ProductionRouter:
    """
    https://docs.djangoproject.com/en/3.0/topics/db/multi-db/
    """
    def db_for_read(self, model, **hints):
        return random.choice([const.READ_DATABASE_NAME, const.WRITE_DATABASE_NAME])

    def db_for_write(self, model, **hints):
        return const.WRITE_DATABASE_NAME

    def allow_relation(self, obj1, obj2, **hints):
        return True

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        return db == const.WRITE_DATABASE_NAME
