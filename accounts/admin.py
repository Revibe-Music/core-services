from django.contrib import admin
from .models import *

# Register your models here.
admin.site.register(CustomUser)
admin.site.register(Profile)
admin.site.register(Social)
admin.site.register(ArtistProfile)
admin.site.register(Device)
