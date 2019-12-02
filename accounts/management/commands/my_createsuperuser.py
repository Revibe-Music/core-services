from django.core.management.base import BaseCommand
from django.conf import settings
from accounts.models import CustomUser


class Command(BaseCommand):

    def handle(self, *args, **options):
        if not CustomUser.objects.filter(username="admin").exists():
            CustomUser.objects.create_superuser("admin", "admin@admin.com", "admin")
            if settings.DEBUG:
                print("<User: 'admin'> user created")
        elif settings.DEBUG:
            print("<User: 'admin'> already exists")
            