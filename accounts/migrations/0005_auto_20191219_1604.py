# Generated by Django 3.0 on 2019-12-19 22:04

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.OAUTH2_PROVIDER_ACCESS_TOKEN_MODEL),
        ('accounts', '0004_auto_20191219_1457'),
    ]

    operations = [
        migrations.AlterField(
            model_name='device',
            name='token',
            field=models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='token_device', to=settings.OAUTH2_PROVIDER_ACCESS_TOKEN_MODEL),
        ),
    ]