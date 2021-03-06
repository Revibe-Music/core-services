# Generated by Django 3.0 on 2020-05-21 20:44

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('customer_success', '0006_auto_20200521_1514'),
    ]

    operations = [
        migrations.AddField(
            model_name='pathway',
            name='users',
            field=models.ManyToManyField(blank=True, help_text='Users that are likely to be interested in the services promoted on this path', limit_choices_to={'programmatic_account': False}, related_name='cs_paths', to=settings.AUTH_USER_MODEL, verbose_name='users'),
        ),
    ]
