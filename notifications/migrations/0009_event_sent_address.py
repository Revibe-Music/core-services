# Generated by Django 3.0 on 2020-05-08 16:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('notifications', '0008_auto_20200508_1140'),
    ]

    operations = [
        migrations.AddField(
            model_name='event',
            name='sent_address',
            field=models.CharField(blank=True, help_text='Email address the message is sent from. If ANY templates of this event use email notifications, this field CANNOT be blank!', max_length=255, null=True, verbose_name='sent address'),
        ),
    ]
