# Generated by Django 3.0 on 2020-03-13 18:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('administration', '0017_auto_20200302_1635'),
    ]

    operations = [
        migrations.AlterField(
            model_name='alert',
            name='category',
            field=models.CharField(choices=[('warn', 'Warning'), ('error', 'Error'), ('info', 'Information'), ('feature', 'New Feature'), ('event', 'Event')], help_text='The type of alert to send to users', max_length=255, verbose_name='alert category'),
        ),
    ]