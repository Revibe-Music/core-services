# Generated by Django 3.0 on 2020-06-04 20:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('referrals', '0007_auto_20200604_1322'),
    ]

    operations = [
        migrations.AlterField(
            model_name='pointcategory',
            name='expiration_interval',
            field=models.CharField(blank=True, choices=[('days', 'Days')], help_text="Time period to use when expiring, time is compared to the time of the user's registration. Leave blank to not expire", max_length=100, null=True, verbose_name='expiration interval'),
        ),
    ]
