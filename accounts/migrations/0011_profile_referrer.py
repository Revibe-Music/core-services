# Generated by Django 3.0 on 2020-02-05 18:29

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0010_auto_20200120_2140'),
    ]

    operations = [
        migrations.AddField(
            model_name='profile',
            name='referrer',
            field=models.ForeignKey(blank=True, default=None, help_text='The user that referred this one', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='referred_users', to=settings.AUTH_USER_MODEL, verbose_name='referrer'),
        ),
    ]
