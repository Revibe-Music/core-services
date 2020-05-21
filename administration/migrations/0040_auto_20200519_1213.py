# Generated by Django 3.0 on 2020-05-19 17:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('administration', '0039_survey'),
    ]

    operations = [
        migrations.AlterField(
            model_name='variable',
            name='category',
            field=models.CharField(blank=True, choices=[('artist-portal', 'Artist Portal Dashboard'), ('browse', 'Browse'), ('cs', 'Customer Success'), ('notifications', 'Notifications'), ('search', 'Search'), ('social', 'Social'), ('util', 'Utils')], help_text='Type of variable this is. Only used for sorting/filtering in the admin portal.', max_length=255, null=True, verbose_name='category'),
        ),
    ]