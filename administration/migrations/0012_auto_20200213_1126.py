# Generated by Django 3.0 on 2020-02-13 17:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('administration', '0011_auto_20200210_1209'),
    ]

    operations = [
        migrations.AlterField(
            model_name='campaign',
            name='destination',
            field=models.CharField(blank=True, choices=[('user', 'Listener'), ('artist', 'Artist'), ('both', 'Artists and Listeners'), ('other', 'Other')], help_text='Target audience', max_length=255, null=True),
        ),
    ]