# Generated by Django 3.0 on 2020-02-18 17:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('content', '0008_album_tags'),
    ]

    operations = [
        migrations.AlterField(
            model_name='album',
            name='tags',
            field=models.ManyToManyField(blank=True, help_text='Associated tags', null=True, related_name='albums', to='content.Tag'),
        ),
        migrations.AlterField(
            model_name='song',
            name='tags',
            field=models.ManyToManyField(blank=True, null=True, related_name='songs', to='content.Tag'),
        ),
    ]
