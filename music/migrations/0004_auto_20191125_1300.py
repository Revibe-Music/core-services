# Generated by Django 2.2.6 on 2019-11-25 19:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('music', '0003_auto_20191125_1235'),
    ]

    operations = [
        migrations.AddField(
            model_name='album',
            name='is_deleted',
            field=models.BooleanField(blank=True, default=False),
        ),
        migrations.AddField(
            model_name='album',
            name='is_displayed',
            field=models.BooleanField(blank=True, default=True),
        ),
    ]
