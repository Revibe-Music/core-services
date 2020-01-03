import random

class ProductionRouter:
    """
    https://docs.djangoproject.com/en/3.0/topics/db/multi-db/
    """
    def db_for_read(self, model, **hints):
        return random.choice(['read', 'write'])
    
    def db_for_write(self, model, **hints):
        return 'write'

    def allow_relation(self, obj1, obj2, **hints):
        return True

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        return True
