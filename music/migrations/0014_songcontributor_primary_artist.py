# Generated by Django 3.0 on 2019-12-13 18:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('music', '0013_auto_20191212_1224'),
    ]

    operations = [
        migrations.AddField(
            model_name='songcontributor',
            name='primary_artist',
            field=models.BooleanField(blank=True, default=False),
        ),
    ]