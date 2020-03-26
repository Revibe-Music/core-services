# Generated by Django 3.0 on 2020-03-26 17:37

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('music', '0004_auto_20200326_1233'),
    ]

    operations = [
        migrations.AlterField(
            model_name='playlist',
            name='followers',
            field=models.ManyToManyField(blank=True, help_text='Users following this playlist. Followers cannot edit a playlist', related_name='followed_playlists', to=settings.AUTH_USER_MODEL, verbose_name='followers'),
        ),
    ]
