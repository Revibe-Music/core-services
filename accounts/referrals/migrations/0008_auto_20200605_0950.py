# Generated by Django 3.0 on 2020-06-05 14:50

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('referrals', '0007_auto_20200604_1322'),
    ]

    operations = [
        migrations.AddField(
            model_name='point',
            name='user',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='points', to=settings.AUTH_USER_MODEL, verbose_name='user'),
        ),
        migrations.AlterField(
            model_name='point',
            name='category',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='assigned_points', to='referrals.PointCategory', verbose_name='category'),
        ),
        migrations.AlterField(
            model_name='point',
            name='referral',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='points', to='referrals.Referral', verbose_name='referral'),
        ),
        migrations.AlterField(
            model_name='pointcategory',
            name='expiration_interval',
            field=models.CharField(blank=True, choices=[('days', 'Days')], help_text="Time period to use when expiring, time is compared to the time of the user's registration. Leave blank to not expire", max_length=100, null=True, verbose_name='expiration interval'),
        ),
    ]
