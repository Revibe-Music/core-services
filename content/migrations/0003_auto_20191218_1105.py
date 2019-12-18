# Generated by Django 3.0 on 2019-12-18 17:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('content', '0002_auto_20191218_0939'),
    ]

    operations = [
        migrations.AddField(
            model_name='albumcontributor',
            name='approved',
            field=models.BooleanField(blank=True, default=True),
        ),
        migrations.AddField(
            model_name='albumcontributor',
            name='pending',
            field=models.BooleanField(blank=True, default=False),
        ),
        migrations.AddField(
            model_name='songcontributor',
            name='approved',
            field=models.BooleanField(blank=True, default=True),
        ),
        migrations.AddField(
            model_name='songcontributor',
            name='pending',
            field=models.BooleanField(blank=True, default=False),
        ),
    ]
