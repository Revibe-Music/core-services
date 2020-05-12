# Generated by Django 3.0 on 2020-05-12 20:55

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('administration', '0038_auto_20200508_1159'),
    ]

    operations = [
        migrations.CreateModel(
            name='Survey',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(help_text='Name of the survey. Must be unique', max_length=255, unique=True, verbose_name='name')),
                ('response', models.TextField(help_text='Survey response. Should be stored as JSON', verbose_name='response')),
                ('date_created', models.DateTimeField(auto_now_add=True)),
                ('last_changed', models.DateTimeField(auto_now=True)),
                ('user', models.ForeignKey(blank=True, help_text='User that filled out the survey', limit_choices_to={'programmatic_account': False}, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='surveys', to=settings.AUTH_USER_MODEL, verbose_name='user')),
            ],
            options={
                'verbose_name': 'survey',
                'verbose_name_plural': 'surveys',
            },
        ),
    ]
