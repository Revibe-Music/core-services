# Generated by Django 3.0 on 2020-02-17 20:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('content', '0007_song_tags'),
    ]

    operations = [
        migrations.AddField(
            model_name='album',
            name='tags',
            field=models.ManyToManyField(help_text='Associated tags', related_name='albums', to='content.Tag'),
        ),
    ]
