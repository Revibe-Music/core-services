# Generated by Django 3.0 on 2020-04-08 00:28

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0026_auto_20200402_1822'),
    ]

    operations = [
        migrations.CreateModel(
            name='Friendship',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('accepted', models.BooleanField(blank=True, default=False, help_text='Whether or not the friend request has been accepted', verbose_name='accepted status')),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('accepted_datetime', models.DateTimeField(blank=True, help_text='The date & time the request was accepted', null=True, verbose_name='accepted datetime')),
                ('first', models.ForeignKey(help_text='First user, the one that instigated the friendship', limit_choices_to={'programmatic_account': False}, on_delete=django.db.models.deletion.CASCADE, related_name='friends_first', to=settings.AUTH_USER_MODEL, verbose_name='first')),
                ('second', models.ForeignKey(help_text='Second user', limit_choices_to={'programmatic_account': False}, on_delete=django.db.models.deletion.CASCADE, related_name='friends_second', to=settings.AUTH_USER_MODEL, verbose_name='second')),
            ],
            options={
                'verbose_name': 'friendship',
                'verbose_name_plural': 'friendships',
            },
        ),
        migrations.AddField(
            model_name='customuser',
            name='friends',
            field=models.ManyToManyField(blank=True, help_text="User's friends", related_name='_customuser_friends_+', through='accounts.Friendship', to=settings.AUTH_USER_MODEL, verbose_name='friends'),
        ),
    ]
