# Generated by Django 3.0 on 2019-12-16 18:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0002_auto_20191215_2047'),
    ]

    operations = [
        migrations.AlterField(
            model_name='customuser',
            name='is_artist',
            field=models.BooleanField(blank=True, default=False, verbose_name='Artist Flag'),
        ),
        migrations.AlterField(
            model_name='customuser',
            name='is_manager',
            field=models.BooleanField(blank=True, default=False, verbose_name='Manager Flag'),
        ),
    ]
