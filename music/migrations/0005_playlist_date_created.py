# Generated by Django 3.0 on 2019-12-05 18:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('music', '0004_auto_20191125_1300'),
    ]

    operations = [
        migrations.AddField(
            model_name='playlist',
            name='date_created',
            field=models.DateField(auto_now_add=True, null=True),
        ),
    ]
