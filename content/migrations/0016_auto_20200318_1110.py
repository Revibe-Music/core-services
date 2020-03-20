# Generated by Django 3.0 on 2020-03-18 16:10

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('content', '0015_placeholdercontribution'),
    ]

    operations = [
        migrations.AddField(
            model_name='placeholdercontribution',
            name='album',
            field=models.ForeignKey(blank=True, help_text='The related album', null=True, on_delete=django.db.models.deletion.CASCADE, related_name='placeholder_contributions', to='content.Album', verbose_name='album'),
        ),
        migrations.AlterField(
            model_name='placeholdercontribution',
            name='song',
            field=models.ForeignKey(blank=True, help_text='The related song', null=True, on_delete=django.db.models.deletion.CASCADE, related_name='placeholder_contributions', to='content.Song', verbose_name='song'),
        ),
    ]