from django.db import models
from django.conf import settings
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db.models.signals import post_save
from django.dispatch import receiver
from music.models import Artist


class CustomUser(AbstractUser):
    artist = models.OneToOneField(Artist, on_delete=models.SET_NULL, related_name='artist_user', null=True, blank=True)

class Profile(models.Model):
    id = models.AutoField(primary_key=True)
    country = models.CharField('Country', max_length=255, null=True)
    # replace with???
    # lat = models.???
    # long = models.???
    dob = models.DateField('Date of Birth', null=True)
    image = models.FileField("Profile Picture", upload_to='images/profiles', null=True)
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=False)


# creates what are basically event listeners to create and save a profile whenever a user is created
# deprecated
# @receiver(post_save, sender=CustomUser)
# def create_user_profile(sender, instance, created, **kwargs):
#     if created:
#         Profile.objects.create(user=instance)

# @receiver(post_save, sender=CustomUser)
# def save_user_profile(sender, instance, **kwargs):
#     instance.profile.save()

class Social(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='user_social')
    platform = models.CharField(max_length=255, null=True)
