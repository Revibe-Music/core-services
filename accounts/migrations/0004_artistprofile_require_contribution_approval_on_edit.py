# Generated by Django 3.0 on 2020-01-08 21:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0003_profile_email'),
    ]

    operations = [
        migrations.AddField(
            model_name='artistprofile',
            name='require_contribution_approval_on_edit',
            field=models.BooleanField(blank=True, default=True),
        ),
    ]
