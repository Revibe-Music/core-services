# Generated by Django 3.0 on 2020-04-07 23:54

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('communication', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='chat',
            options={'verbose_name': 'chat', 'verbose_name_plural': 'chats'},
        ),
        migrations.AlterModelOptions(
            name='message',
            options={'verbose_name': 'message', 'verbose_name_plural': 'messages'},
        ),
    ]
