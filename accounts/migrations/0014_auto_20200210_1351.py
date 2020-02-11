# Generated by Django 3.0 on 2020-02-10 19:51

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0013_socialmedia'),
    ]

    operations = [
        migrations.AlterField(
            model_name='socialmedia',
            name='artist_profile',
            field=models.ForeignKey(help_text="Account's artist", on_delete=django.db.models.deletion.CASCADE, related_name='social_media', to='accounts.ArtistProfile'),
        ),
    ]