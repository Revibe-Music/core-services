# Generated by Django 2.2.6 on 2019-11-01 16:54

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('revibe_api', '0004_artist_user'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='artist',
            name='user',
        ),
    ]