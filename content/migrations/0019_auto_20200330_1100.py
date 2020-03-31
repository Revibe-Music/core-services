# Generated by Django 3.0 on 2020-03-30 16:00

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('content', '0018_auto_20200323_1458'),
    ]

    operations = [
        migrations.AlterField(
            model_name='song',
            name='uploaded_by',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='song_uploaded_by', to='content.Artist'),
        ),
    ]