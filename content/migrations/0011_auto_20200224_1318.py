# Generated by Django 3.0 on 2020-02-24 19:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('content', '0010_auto_20200218_1124'),
    ]

    operations = [
        migrations.AddField(
            model_name='song',
            name='streams_last_month',
            field=models.IntegerField(default=0, help_text='Number of streams recorded in DynamoDB in the last 30 days. Will be updated automatically.', verbose_name='streams in the last 30 days'),
        ),
        migrations.AddField(
            model_name='song',
            name='streams_last_week',
            field=models.IntegerField(blank=True, default=0, help_text='Number of streams recorded in DynamoDB in the last 7 days. Will be updated automatically.', verbose_name='streams in the last 7 days'),
        ),
        migrations.AddField(
            model_name='song',
            name='streams_this_year',
            field=models.IntegerField(default=0, help_text='Number of streams recorded in DynamoDB during this calendar year. Will be updated automatically.', verbose_name='streams this calendar year'),
        ),
        migrations.AddField(
            model_name='song',
            name='streams_yesterday',
            field=models.IntegerField(blank=True, default=0, help_text='Number of streams recorded in DynamoDB yesterday. Will be updated automatically.', verbose_name='streams yesterday'),
        ),
    ]
