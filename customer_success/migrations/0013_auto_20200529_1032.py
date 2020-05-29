# Generated by Django 3.0 on 2020-05-29 15:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('customer_success', '0012_auto_20200528_1414'),
    ]

    operations = [
        migrations.AddField(
            model_name='action',
            name='recur_interval_period',
            field=models.CharField(blank=True, choices=[('days', 'Day(s)')], help_text='The type of time period to use for recurrance', max_length=50, null=True, verbose_name='time period'),
        ),
        migrations.AddField(
            model_name='action',
            name='recur_number_of_periods',
            field=models.IntegerField(blank=True, help_text="The number of interval periods to wait before resending this action's notification.", null=True, verbose_name='number of periods'),
        ),
        migrations.AddField(
            model_name='action',
            name='recurring',
            field=models.BooleanField(default=False, help_text='Marks the action as recurring. This action can notify the users after the users has performed the action', verbose_name='recurring'),
        ),
    ]
