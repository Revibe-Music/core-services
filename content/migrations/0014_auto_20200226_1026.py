# Generated by Django 3.0 on 2020-02-26 16:26

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('content', '0013_song_streams_all_time'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='song',
            name='streams_all_time',
        ),
        migrations.RemoveField(
            model_name='song',
            name='streams_last_month',
        ),
        migrations.RemoveField(
            model_name='song',
            name='streams_last_week',
        ),
        migrations.RemoveField(
            model_name='song',
            name='streams_this_year',
        ),
        migrations.RemoveField(
            model_name='song',
            name='streams_yesterday',
        ),
    ]