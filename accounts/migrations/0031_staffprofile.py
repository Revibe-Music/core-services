# Generated by Django 3.0 on 2020-05-06 15:07

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0030_customuser_date_registered'),
    ]

    operations = [
        migrations.CreateModel(
            name='StaffProfile',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('job_title', models.CharField(blank=True, help_text="Staff's job title", max_length=255, null=True, verbose_name='job title')),
                ('display_name', models.CharField(blank=True, help_text='Staff display name. Used for things like blog posts', max_length=255, null=True, verbose_name='display name')),
                ('pay_type', models.CharField(blank=True, choices=[('salary', 'Salary'), ('wage', 'Hourly Wage')], help_text='How the staff member is paid', max_length=20, null=True, verbose_name='pay type')),
                ('pay', models.DecimalField(blank=True, decimal_places=2, help_text='How much the staff member is paid, either hourly or yearly', max_digits=11, null=True, verbose_name='pay')),
                ('start_date', models.DateTimeField(blank=True, help_text="Staff's start date at Revibe", null=True, verbose_name='start date')),
                ('job_start_date', models.DateTimeField(blank=True, help_text='Date staff member started their current role', null=True, verbose_name='job start date')),
                ('supervisor', models.ForeignKey(blank=True, help_text="Staff member's supervisor", limit_choices_to={'is_staff': True, 'programmatic_account': False, 'temporary_account': False}, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='reports', to=settings.AUTH_USER_MODEL, verbose_name='supervisor')),
                ('user', models.OneToOneField(help_text='User account', limit_choices_to={'is_staff': True, 'programmatic_account': False, 'temporary_account': False}, on_delete=django.db.models.deletion.CASCADE, related_name='staff_profile', to=settings.AUTH_USER_MODEL, verbose_name='user')),
            ],
            options={
                'verbose_name': 'staff account',
                'verbose_name_plural': 'staff accounts',
            },
        ),
    ]
