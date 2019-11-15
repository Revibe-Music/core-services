# Generated by Django 2.2.6 on 2019-11-15 00:09

from django.db import migrations, models
import music.models
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('music', '0003_auto_20191114_1728'),
    ]

    operations = [
        migrations.AlterField(
            model_name='album',
            name='image',
            field=models.FileField(upload_to='images/albums', verbose_name='Album Image'),
        ),
        migrations.AlterField(
            model_name='song',
            name='file',
            field=models.FileField(null=True, upload_to=music.models.rename_file, verbose_name='Song'),
        ),
        migrations.AlterField(
            model_name='song',
            name='uri',
            field=models.UUIDField(default=uuid.uuid4, editable=False, unique=True, verbose_name='URI'),
        ),
    ]
