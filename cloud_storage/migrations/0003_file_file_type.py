# Generated by Django 3.0 on 2020-03-23 19:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cloud_storage', '0002_auto_20200323_1421'),
    ]

    operations = [
        migrations.AddField(
            model_name='file',
            name='file_type',
            field=models.CharField(blank=True, choices=[('audio', 'Audio'), ('image', 'Image'), ('other', 'Other')], help_text='The kind of file this is. Helps with filtering and sorting. Not required.', max_length=100, null=True, verbose_name='file type'),
        ),
    ]
