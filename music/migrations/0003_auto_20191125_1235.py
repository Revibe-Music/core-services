# Generated by Django 2.2.6 on 2019-11-25 18:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('music', '0002_auto_20191125_1212'),
    ]

    operations = [
        migrations.AddField(
            model_name='song',
            name='is_deleted',
            field=models.BooleanField(blank=True, default=False),
        ),
        migrations.AddField(
            model_name='song',
            name='is_displayed',
            field=models.BooleanField(blank=True, default=True),
        ),
    ]