# Generated by Django 2.2.6 on 2019-11-16 20:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('music', '0005_song_genre'),
    ]

    operations = [
        migrations.CreateModel(
            name='SongAnalysis',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
            ],
        ),
    ]
