# Generated by Django 3.0 on 2020-01-07 15:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='artistprofile',
            name='allow_contributors_to_edit_contributions',
            field=models.BooleanField(blank=True, default=False),
        ),
    ]
