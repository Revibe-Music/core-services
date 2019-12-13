# Generated by Django 3.0 on 2019-12-09 16:14

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('music', '0008_auto_20191205_1603'),
    ]

    operations = [
        migrations.AddField(
            model_name='album',
            name='date_added',
            field=models.DateTimeField(auto_now_add=True, null=True),
        ),
        migrations.AddField(
            model_name='album',
            name='date_published',
            field=models.DateField(blank=True, default=datetime.datetime.now, null=True),
        ),
        migrations.AddField(
            model_name='album',
            name='last_changed',
            field=models.DateTimeField(auto_now=True, null=True),
        ),
    ]