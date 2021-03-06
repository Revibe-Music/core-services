# Generated by Django 3.0 on 2020-06-17 20:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('notifications', '0021_auto_20200617_1059'),
    ]

    operations = [
        migrations.AlterField(
            model_name='notificationtemplate',
            name='medium',
            field=models.CharField(choices=[('email', 'Email'), ('in-app', 'In-App'), ('push', 'Push'), ('sms', 'Text Message')], help_text='The medium by which to send the notification', max_length=255, verbose_name='medium'),
        ),
    ]
