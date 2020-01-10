# Generated by Django 3.0 on 2020-01-10 18:11

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('administration', '0003_auto_20200110_1211'),
        ('accounts', '0005_artistprofile_hide_all_content'),
    ]

    operations = [
        migrations.AddField(
            model_name='profile',
            name='campaign',
            field=models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.SET_NULL, to='administration.Campaign'),
        ),
    ]
