# Generated by Django 3.0 on 2020-03-20 21:18

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('marketplace', '0001_initial'),
        ('content', '0016_auto_20200318_1110'),
    ]

    operations = [
        migrations.AddField(
            model_name='image',
            name='good',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='images', to='marketplace.Good'),
        ),
        migrations.AddField(
            model_name='track',
            name='good',
            field=models.ForeignKey(blank=True, help_text='Marketplace item', null=True, on_delete=django.db.models.deletion.CASCADE, related_name='audio_files', to='marketplace.Good', verbose_name='good'),
        ),
        migrations.AlterField(
            model_name='track',
            name='song',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='tracks', to='content.Song'),
        ),
    ]
