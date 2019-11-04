# Generated by Django 2.2.6 on 2019-11-04 00:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('music', '0003_auto_20191103_1720'),
    ]

    operations = [
        migrations.AddField(
            model_name='song',
            name='beats_per_minute',
            field=models.IntegerField(blank=True, null=True, verbose_name='Beats per Minute'),
        ),
        migrations.AddField(
            model_name='song',
            name='genre',
            field=models.CharField(blank=True, max_length=255, null=True, verbose_name='Genre'),
        ),
        migrations.AlterField(
            model_name='song',
            name='duration',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=6, null=True, verbose_name='Duration'),
        ),
    ]
