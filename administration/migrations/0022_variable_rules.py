# Generated by Django 3.0 on 2020-03-16 21:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('administration', '0021_variable'),
    ]

    operations = [
        migrations.AddField(
            model_name='variable',
            name='rules',
            field=models.TextField(blank=True, help_text="Detail how to set up this value. Some variables require string formatting, such as 'mobile_app_share_text'.", null=True, verbose_name='variable rules'),
        ),
    ]
