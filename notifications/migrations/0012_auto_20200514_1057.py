# Generated by Django 3.0 on 2020-05-14 15:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('notifications', '0011_delete_reminder'),
    ]

    operations = [
        migrations.AlterField(
            model_name='event',
            name='desired_action',
            field=models.CharField(blank=True, help_text='Action the user is desired to take after receiving this notification', max_length=255, null=True, verbose_name='desired action'),
        ),
    ]