from django.core.management.base import BaseCommand
from django.conf import settings
from accounts.models import CustomUser


class Command(BaseCommand):

    def handle(self, *args, **options):
        username = 'admin' if settings.DEBUG else 'fjfnoswIvwoloNWFnw'
        password = 'admin' if settings.DEBUG else '03f2mawfv-02qmrpI(FJO#ia;fo4i3nrf89anoda9'
        if not CustomUser.objects.filter(username=username).exists():
            CustomUser.objects.create_superuser(username, "admin@admin.com", password)
            if settings.DEBUG:
                print("<User: 'admin'> user created")
        elif settings.DEBUG:
            print("<User: 'admin'> already exists")
            