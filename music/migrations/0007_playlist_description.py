# Generated by Django 3.0 on 2020-04-07 23:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('music', '0006_auto_20200330_1856'),
    ]

    operations = [
        migrations.AddField(
            model_name='playlist',
            name='description',
            field=models.TextField(blank=True, help_text='Playlist description', null=True, verbose_name='description'),
        ),
    ]
