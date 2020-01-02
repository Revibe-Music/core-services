from django.conf import settings

def debug_print(thing):
    if settings.DEBUG:
        print(thing)