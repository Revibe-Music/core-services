from django.core.management.base import BaseCommand
from django.conf import settings
from oauth2_provider.models import Application

class Command(BaseCommand):

    def handle(self, *args, **kwargs):
        if not Application.objects.filter(name="Revibe First Party Application").exists():
            Application.objects.create(client_type="confidential", authorization_grant_type="password", name="Revibe First Party Application")
            if settings.DEBUG:
                print("<Application: 'Revibe First Party Application'> application created")
        elif settings.DEBUG:
            print("<Application: 'Revibe First Party Application'> already exists")
