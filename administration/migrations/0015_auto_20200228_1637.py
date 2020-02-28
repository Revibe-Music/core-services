# Generated by Django 3.0 on 2020-02-28 22:37

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('administration', '0014_alert'),
    ]

    operations = [
        migrations.CreateModel(
            name='AlertSeen',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('has_seen', models.BooleanField(blank=True, default=True, help_text='Indicates that the user has seen the alert', verbose_name='has seen')),
                ('alert', models.ForeignKey(help_text='Related system alert', on_delete=django.db.models.deletion.CASCADE, related_name='alert_seen', to='administration.Alert', verbose_name='alert')),
                ('user', models.ForeignKey(help_text='User that saw the alert', on_delete=django.db.models.deletion.CASCADE, related_name='alert_seen', to=settings.AUTH_USER_MODEL, verbose_name='user')),
            ],
            options={
                'verbose_name': 'alert seen',
                'verbose_name_plural': 'alerts seen',
            },
        ),
        migrations.AddField(
            model_name='alert',
            name='users_seen',
            field=models.ManyToManyField(help_text='The users that have seen this alert', related_name='alerts_seen', through='administration.AlertSeen', to=settings.AUTH_USER_MODEL),
        ),
    ]
