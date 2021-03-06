# Generated by Django 3.0 on 2020-03-23 19:58

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('cloud_storage', '0004_auto_20200323_1458'),
        ('marketplace', '0004_auto_20200323_1418'),
    ]

    operations = [
        migrations.AddField(
            model_name='good',
            name='file',
            field=models.ForeignKey(blank=True, help_text='Relevant file. Not required.', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='goods', to='cloud_storage.File', verbose_name='file'),
        ),
    ]
