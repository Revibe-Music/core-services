# Generated by Django 3.0 on 2020-05-07 17:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('notifications', '0006_auto_20200507_1041'),
    ]

    operations = [
        migrations.AddField(
            model_name='notification',
            name='seen',
            field=models.BooleanField(blank=True, default=False, help_text='The notified user has seen the notification', verbose_name='seen'),
        ),
    ]
