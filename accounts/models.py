from django.db import models
from django.conf import settings
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db.models.signals import post_save
from django.dispatch import receiver
from music.models import Artist


class CustomUser(AbstractUser):
    artist = models.OneToOneField(Artist, on_delete=models.SET_NULL, related_name='artist_user', null=True, blank=True)
    manager = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True)
    is_artist = models.BooleanField('Artist Flag', null=False, blank=False, default=False)
    is_manager = models.BooleanField('Manager Flag', null=False, blank=False, default=False)

class Profile(models.Model):
    id = models.AutoField(primary_key=True)
    country = models.CharField('Country', max_length=255, null=True, blank=True)
    # replace with???
    # lat = models.???
    # long = models.???
    dob = models.DateField('Date of Birth', null=True, blank=True)
    image = models.FileField("Profile Picture", upload_to='images/profiles', null=True, blank=True)
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=False)

class Social(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='user_social')
    platform = models.CharField(max_length=255, null=True)