# Generated by Django 3.0 on 2020-02-17 17:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('content', '0006_tag'),
    ]

    operations = [
        migrations.AddField(
            model_name='song',
            name='tags',
            field=models.ManyToManyField(related_name='songs', to='content.Tag'),
        ),
    ]
