# Generated by Django 3.0 on 2020-04-30 17:25

from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('content', '0023_auto_20200428_1203'),
    ]

    operations = [
        migrations.AddField(
            model_name='song',
            name='isrc_code',
            field=models.CharField(blank=True, help_text='Internationally recognized identifier for the song', max_length=255, null=True, verbose_name='ISRC code'),
        ),
        migrations.AlterField(
            model_name='song',
            name='duration',
            field=models.DecimalField(blank=True, decimal_places=2, help_text='Duration of the song in seconds', max_digits=6, null=True, verbose_name='duration'),
        ),
        migrations.AlterField(
            model_name='song',
            name='title',
            field=models.CharField(max_length=255, verbose_name='title'),
        ),
        migrations.AlterField(
            model_name='song',
            name='uri',
            field=models.CharField(default=uuid.uuid4, editable=False, help_text='Secondary unique identifier', max_length=255, unique=True, verbose_name='URI'),
        ),
    ]
