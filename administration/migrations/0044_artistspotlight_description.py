# Generated by Django 3.0 on 2020-05-22 15:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('administration', '0043_auto_20200522_1042'),
    ]

    operations = [
        migrations.AddField(
            model_name='artistspotlight',
            name='description',
            field=models.TextField(blank=True, help_text='Human-readable explanation of the Spotlight', null=True, verbose_name='description'),
        ),
    ]
